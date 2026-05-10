from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import stripe

from .models import Course, Enrollment, LessonProgress, ModuleLesson


def women_home(request):
    online_courses = Course.objects.filter(is_active=True, mode=Course.MODE_ONLINE).annotate(
        modules_count=Count('modules', distinct=True),
        lessons_count=Count('modules__lessons', distinct=True),
    ).order_by('-created_at')[:6]
    
    offline_courses = Course.objects.filter(is_active=True, mode=Course.MODE_OFFLINE).annotate(
        modules_count=Count('modules', distinct=True),
        lessons_count=Count('modules__lessons', distinct=True),
    ).order_by('-created_at')[:6]
    
    return render(
        request,
        'women/home.html',
        {
            'online_courses': online_courses,
            'offline_courses': offline_courses,
        },
    )


def women_about(request):
    return render(request, 'women/about.html')


def women_mission_vision(request):
    return render(request, 'women/mission_vision.html')


def course_list(request):
    courses = Course.objects.filter(is_active=True).annotate(
        modules_count=Count('modules', distinct=True),
        lessons_count=Count('modules__lessons', distinct=True),
    ).order_by('title')

    mode = request.GET.get('mode', '').strip()
    if mode in [Course.MODE_ONLINE, Course.MODE_OFFLINE]:
        courses = courses.filter(mode=mode)

    return render(request, 'women/course_list.html', {'courses': courses, 'selected_mode': mode})


def course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons'),
        id=course_id,
        is_active=True,
    )

    enrollment = None
    progress_by_lesson_id = set()
    total_lessons = ModuleLesson.objects.filter(module__course=course).count()
    completed_lessons = 0

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment:
            progress_by_lesson_id = set(
                LessonProgress.objects.filter(enrollment=enrollment, completed=True)
                .values_list('lesson_id', flat=True)
            )
            completed_lessons = len(progress_by_lesson_id)

    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    return render(
        request,
        'women/course_detail.html',
        {
            'course': course,
            'enrollment': enrollment,
            'progress_by_lesson_id': progress_by_lesson_id,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent,
        },
    )


@login_required
def enroll_course(request, course_id):
    from django.conf import settings
    
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if existing_enrollment and existing_enrollment.is_paid:
        messages.info(request, f'You are already enrolled in "{course.title}".')
        return redirect('women:course_detail', course_id=course.id)

    # Free course: direct enrollment
    if course.fee == 0:
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': Enrollment.STATUS_ACTIVE, 'payment_confirmed_at': timezone.now()},
        )
        if created:
            messages.success(request, f'You have enrolled in "{course.title}" for free.')
        return redirect('women:course_detail', course_id=course.id)

    # Paid course: redirect to Stripe checkout
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'bdt',
                        'product_data': {
                            'name': course.title,
                            'description': course.short_description,
                        },
                        'unit_amount': int(course.fee * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=(
                request.build_absolute_uri(f'/women/payment-success/?course_id={course.id}&session_id=')
                + '{CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri(f'/women/courses/{course.id}/'),
            customer_email=request.user.email,
            metadata={'user_id': request.user.id, 'course_id': course.id},
        )

        # Create pending enrollment
        enrollment, _ = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'status': Enrollment.STATUS_PENDING,
                'stripe_session_id': checkout_session.id,
            },
        )
        if not enrollment.stripe_session_id:
            enrollment.stripe_session_id = checkout_session.id
            enrollment.status = Enrollment.STATUS_PENDING
            enrollment.save()

        return redirect(checkout_session.url, code=303)
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('women:course_detail', course_id=course.id)


@login_required
def mark_lesson_complete(request, lesson_id):
    if request.method != 'POST':
        return redirect('women:my_learning')

    lesson = get_object_or_404(ModuleLesson.objects.select_related('module__course'), id=lesson_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=lesson.module.course).first()

    if not enrollment:
        messages.error(request, 'Please enroll in the course first.')
        return redirect('women:course_detail', course_id=lesson.module.course.id)

    # Check if payment is confirmed for paid courses
    if not enrollment.is_paid:
        messages.error(request, 'Please complete payment to access this course.')
        return redirect('women:course_detail', course_id=lesson.module.course.id)

    progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    if not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save(update_fields=['completed', 'completed_at'])

    total_lessons = ModuleLesson.objects.filter(module__course=enrollment.course).count()
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        lesson__module__course=enrollment.course,
        completed=True,
    ).count()

    if total_lessons > 0 and completed_lessons == total_lessons and enrollment.completed_at is None:
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=['completed_at'])
        messages.success(request, f'Congratulations! You completed "{enrollment.course.title}".')
    else:
        messages.success(request, 'Lesson marked as complete.')

    return redirect('women:course_detail', course_id=enrollment.course.id)


@login_required
def my_learning(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')

    enrollment_rows = []
    for enrollment in enrollments:
        total_lessons = ModuleLesson.objects.filter(module__course=enrollment.course).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson__module__course=enrollment.course,
            completed=True,
        ).count()
        progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        enrollment_rows.append({
            'enrollment': enrollment,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent,
        })

    return render(request, 'women/my_learning.html', {'enrollment_rows': enrollment_rows})


@login_required
def payment_success(request):
    """Handle Stripe payment success callback."""
    from django.conf import settings
    
    session_id = request.GET.get('session_id')
    course_id = request.GET.get('course_id')

    if not session_id or not course_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('women:course_list')

    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Query for existing enrollment regardless of payment status
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course,
    ).first()

    if not enrollment:
        # Enrollment may not exist yet; create it as pending
        enrollment = Enrollment.objects.create(
            user=request.user,
            course=course,
            status=Enrollment.STATUS_PENDING,
            stripe_session_id=session_id,
        )

    # Verify payment with Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            # Update enrollment to active with payment confirmed
            enrollment.status = Enrollment.STATUS_ACTIVE
            enrollment.payment_confirmed_at = timezone.now()
            enrollment.stripe_session_id = session_id
            enrollment.save()
            messages.success(request, f'Payment confirmed! You now have access to "{course.title}".')
            return redirect('women:course_detail', course_id=course.id)
        else:
            messages.warning(request, 'Payment not confirmed. Please try again.')
            if enrollment.status == Enrollment.STATUS_PENDING:
                enrollment.delete()
            return redirect('women:course_detail', course_id=course.id)
    except stripe.error.StripeError as e:
        messages.error(request, f'Error verifying payment: {str(e)}')
        return redirect('women:course_list')
