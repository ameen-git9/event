# event_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from event_app.models import CustomUser, Event, Registration, Payment
from event_app.forms import AddBoyForm, EventForm, RegistrationForm, BoyProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.conf import settings
import razorpay
from django.core.paginator import Paginator
from django.db import models





# --------------------------
# Landing Page
# --------------------------
class LandingPageView(TemplateView):
    template_name = "home.html"


# --------------------------
# Authentication
# --------------------------
class StaffLoginView(View):
    template_name = "staff_login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        staff_id = request.POST.get("staff_id")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, staff_id=staff_id, username=username, password=password)

        if user and user.is_staff_user:
            login(request, user)
            return redirect("staff_dashboard")

        messages.error(request, "Invalid Staff Credentials")
        return redirect("staff_login")


class BoyLoginView(View):
    template_name = "boy_login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        boy_id = request.POST.get("boy_id")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # First-time login (no password)
        if password.strip() == "":
            user = CustomUser.objects.filter(boy_id=boy_id, username=username, is_boy_user=True).first()
            if user:
                return redirect("set_password", user_id=user.id)

            messages.error(request, "Invalid Login. User not found.")
            return redirect("boy_login")

        # Normal login
        user = authenticate(request, boy_id=boy_id, username=username, password=password)
        if user and user.is_boy_user:
            login(request, user)
            return redirect("boy_dashboard")

        messages.error(request, "Invalid Credentials")
        return redirect("boy_login")


class SetPasswordView(View):
    template_name = "set_password.html"

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        return render(request, self.template_name, {"user": user})

    def post(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("set_password", user_id=user.id)

        user.set_password(password)
        user.first_time_login = False
        user.save()

        messages.success(request, "Password set successfully. Please login.")
        return redirect("boy_login")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("landing_page")


# --------------------------
# Access Mixins
# --------------------------
class StaffOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff_user:
            messages.error(request, "Access denied.")
            return redirect("staff_login")
        return super().dispatch(request, *args, **kwargs)


class BoyOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_boy_user:
            messages.error(request, "Access denied.")
            return redirect("boy_login")
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# STAFF DASHBOARD
# --------------------------
class StaffDashboardView(LoginRequiredMixin, StaffOnlyMixin, View):
    template_name = "staff/dashboard.html"

    def get(self, request):
        total_boys = CustomUser.objects.filter(is_boy_user=True).count()
        total_events = Event.objects.count()
        upcoming_events = Event.objects.filter(event_status="upcoming").count()
        pending_payments = Payment.objects.filter(payment_status="Pending").count()
        upcoming_events_list = Event.objects.filter(event_status="upcoming").order_by('date')[:5]

        context = {
            "staff": request.user,
            "total_boys": total_boys,
            "total_events": total_events,
            "upcoming_events": upcoming_events,
            "pending_payments": pending_payments,
            "upcoming_events_list": upcoming_events_list,
        }
        return render(request, self.template_name, context)


# --------------------------
# Staff → Manage Boys
# --------------------------
class AddBoyView(LoginRequiredMixin, StaffOnlyMixin, View):
    template_name = "staff/add_boy.html"

    def get(self, request):
        form = AddBoyForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AddBoyForm(request.POST)
        if form.is_valid():
            boy = form.save(commit=False)
            boy.is_boy_user = True
            boy.first_time_login = True
            boy.set_unusable_password()
            boy.save()

            messages.success(request, "Catering boy added successfully.")
            return redirect("view_boys")

        return render(request, self.template_name, {"form": form})


class BoysListView(LoginRequiredMixin, StaffOnlyMixin, View):
    template_name = "staff/boys_list.html"

    def get(self, request):
        boys = CustomUser.objects.filter(is_boy_user=True).order_by("boy_id")
        return render(request, self.template_name, {"boys": boys})



class EditBoyView(LoginRequiredMixin, StaffOnlyMixin, UpdateView):
    model = CustomUser
    form_class = AddBoyForm
    template_name = "staff/edit_boy.html"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return CustomUser.objects.filter(is_boy_user=True)

    def get_success_url(self):
        messages.success(self.request, "Catering boy updated.")
        return reverse("view_boys")


# --------------------------
# Staff → Create Event
# --------------------------
class CreateEventView(LoginRequiredMixin, StaffOnlyMixin, View):
    template_name = "staff/create_event.html"

    def get(self, request):
        form = EventForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EventForm(request.POST, request.FILES)   # << FIX HERE
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully.")
            return redirect("view_events")

        return render(request, self.template_name, {"form": form})



# --------------------------
# View All Events
# --------------------------


class EventsListView(LoginRequiredMixin, View):
    template_name = "events/events_list.html"

    def get(self, request):

        query = request.GET.get("q")
        status_filter = request.GET.get("status")
        sort = request.GET.get("sort", "date_asc")  # default sorting

        events = Event.objects.all()

        # SEARCH
        if query:
            events = events.filter(title__icontains=query)

        # STATUS FILTER
        if status_filter and status_filter != "all":
            events = events.filter(event_status=status_filter)

        # SORTING OPTIONS
        if sort == "date_asc":                 # Oldest first
            events = events.order_by("date")
        elif sort == "date_desc":              # Newest first
            events = events.order_by("-date")
        elif sort == "title_asc":              # A → Z
            events = events.order_by("title")
        elif sort == "title_desc":             # Z → A
            events = events.order_by("-title")

        # PAGINATION (10 per page)
        paginator = Paginator(events, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            "page_obj": page_obj,
            "events": page_obj,    # backwards compatibility
        })




# --------------------------
# Event Detail Page
# --------------------------
class EventDetailView(LoginRequiredMixin, View):
    template_name = "events/event_detail.html"

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        registrations = Registration.objects.filter(event=event).select_related("boy")

        user_registered = None
        if request.user.is_boy_user:
            user_registered = registrations.filter(boy=request.user).first()

        context = {
            "event": event,
            "registrations": registrations,
            "user_registered": user_registered,
            "available_seats": event.available_seats
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if not request.user.is_staff_user:
            return HttpResponseForbidden("Only staff can perform this action.")

        action = request.POST.get("action")

        if action == "mark_completed":
            event.event_status = "completed"
            event.save()
            messages.success(request, "Event marked completed.")

        elif action == "simulate_pay_all":
            regs = Registration.objects.filter(event=event)
            count = 0
            for reg in regs:
                pay, _ = Payment.objects.get_or_create(
                    registration=reg,
                    defaults={"amount": event.payment_per_boy}
                )
                if pay.payment_status != "Paid":
                    pay.payment_status = "Paid"
                    pay.paid_at = timezone.now()
                    pay.payment_id = f"SIM_{pay.id}_{int(timezone.now().timestamp())}"
                    pay.save()
                count += 1

            messages.success(request, f"Payments simulated for {count} boys.")

        return redirect("event_detail", pk=event.pk)


# --------------------------
# Edit/Delete Event
# --------------------------
class EditEventView(LoginRequiredMixin, StaffOnlyMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/edit_event.html"
    pk_url_kwarg = "pk"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EventForm(request.POST, request.FILES, instance=self.object)  # FIX
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated.")
            return redirect("view_events")
        return render(request, self.template_name, {"form": form})


class DeleteEventView(LoginRequiredMixin, StaffOnlyMixin, DeleteView):
    model = Event
    template_name = "events/confirm_delete_event.html"
    success_url = reverse_lazy("view_events")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Event deleted.")
        return super().delete(request, *args, **kwargs)


# --------------------------
# Boy Registration for Event
# --------------------------
class RegisterForEventView(LoginRequiredMixin, BoyOnlyMixin, View):
    template_name = "events/register_confirm.html"

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.available_seats <= 0:
            messages.error(request, "No seats available.")
            return redirect("event_detail", pk=pk)

        if Registration.objects.filter(event=event, boy=request.user).exists():
            messages.info(request, "Already registered.")
            return redirect("event_detail", pk=pk)

        return render(request, self.template_name, {"event": event})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.available_seats <= 0:
            messages.error(request, "No seats available.")
            return redirect("event_detail", pk=pk)

        last = Registration.objects.filter(event=event).order_by("-seat_number").first()
        next_seat = 1 if not last else last.seat_number + 1

        reg = Registration.objects.create(
            boy=request.user,
            event=event,
            seat_number=next_seat
        )

        Payment.objects.create(
            registration=reg,
            amount=event.payment_per_boy,
            payment_status="Pending"
        )

        messages.success(request, f"Registered! Your seat number is {next_seat}.")
        return redirect("event_detail", pk=pk)


# --------------------------
# BOY Dashboard
# --------------------------
class BoyDashboardView(LoginRequiredMixin, BoyOnlyMixin, View):
    template_name = "boy/dashboard.html"

    def get(self, request):
        regs = Registration.objects.filter(boy=request.user).select_related("event")
        payments = Payment.objects.filter(registration__boy=request.user)
        return render(request, self.template_name, {"registrations": regs, "payments": payments})


# --------------------------
# Payment Simulation (Staff)
# --------------------------
class SimulatePaymentView(LoginRequiredMixin, StaffOnlyMixin, View):
    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, pk=payment_id)
        payment.payment_status = "Paid"
        payment.paid_at = timezone.now()
        payment.payment_id = f"SIM_{payment.id}_{int(timezone.now().timestamp())}"
        payment.save()

        messages.success(request, "Payment simulated.")
        return redirect("payment_history")


# --------------------------
# Payment History
# --------------------------
class PaymentHistoryView(LoginRequiredMixin, StaffOnlyMixin, View):
    template_name = "staff/payment_history.html"

    def get(self, request):
        payments = Payment.objects.select_related('registration__boy', 'registration__event').order_by('-id')
        return render(request, self.template_name, {"payments": payments})

class CreateRazorpayOrderView(LoginRequiredMixin, StaffOnlyMixin, View):
    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, pk=payment_id)
        event = payment.registration.event

        if event.event_status != "completed":
            messages.error(request, "Event is not completed.")
            return redirect("event_detail", pk=event.pk)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order = client.order.create({
            "amount": payment.amount * 100,
            "currency": "INR",
            "receipt": f"order_rcptid_{payment.id}",
            "payment_capture": 1
        })

        payment.payment_id = order["id"]       # Razorpay ORDER ID
        payment.save()

        return render(request, "staff/razorpay_checkout.html", {
            "payment": payment,
            "order": order,
            "key_id": settings.RAZORPAY_KEY_ID,
        })
    

class RazorpayCallbackView(View):
    def post(self, request):
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }

        # VERIFY SIGNATURE
        try:
            client.utility.verify_payment_signature(params_dict)
        except:
            messages.error(request, "Payment Verification Failed")
            return redirect("payment_history")

        # SUCCESS → Update DB
        payment = Payment.objects.get(payment_id=razorpay_order_id)
        payment.payment_status = "Paid"
        payment.paid_at = timezone.now()
        payment.payment_id = razorpay_payment_id  # store final id
        payment.save()

        # ----------------------------
        # SEND SUCCESS EMAIL TO BOY
        # ----------------------------
        try:
            from django.core.mail import send_mail

            boy = payment.registration.boy
            event = payment.registration.event

            if boy.email:
                print("📧 EMAIL TRIGGERED FOR:", boy.email)
                send_mail(
                    subject="Payment Successful",
                    message=(
                        f"Hello {boy.username},\n\n"
                        f"You have received a payment of ₹{payment.amount} "
                        f"for the event: {event.title}.\n\n"
                        "Thank you for your work!\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[boy.email],
                    fail_silently=True,
                )
        except:
            pass  # email fail safe

        messages.success(request, "Payment Successful & Email Sent!")
        return redirect("payment_history")
        



class RazorpayFailView(View):
    def get(self, request):
        messages.error(request, "Payment Failed or Cancelled.")
        return redirect("payment_history")





# BoyOnlyMixin and StaffOnlyMixin already exist in your file.

class BoyProfileView(LoginRequiredMixin, BoyOnlyMixin, View):
    template_name = "boy/profile.html"

    def get(self, request):
        user = request.user
        form = BoyProfileForm(instance=user)

        # Stats
        registrations = Registration.objects.filter(boy=user).select_related("event").order_by("-registration_date")
        payments = Payment.objects.filter(registration__boy=user).select_related("registration__event").order_by("-paid_at")

        total_earnings = payments.filter(payment_status="Paid").aggregate(
            total=models.Sum("amount")
        )["total"] or 0

        context = {
            "form": form,
            "target_user": user,
            "registrations": registrations,
            "payments": payments,
            "total_earnings": total_earnings,
            "is_staff_view": False,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user

        form = BoyProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():

            # save basic fields
            updated_user = form.save(commit=False)

            # handle profile picture manually
            if "profile_pic" in request.FILES:
                updated_user.profile_pic = request.FILES["profile_pic"]

            updated_user.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("boy_profile")

        # If form invalid, load stats again
        registrations = Registration.objects.filter(boy=user).select_related("event").order_by("-registration_date")
        payments = Payment.objects.filter(registration__boy=user).select_related("registration__event").order_by("-paid_at")

        total_earnings = payments.filter(payment_status="Paid").aggregate(
            total=models.Sum("amount")
        )["total"] or 0

        context = {
            "form": form,
            "target_user": user,
            "registrations": registrations,
            "payments": payments,
            "total_earnings": total_earnings,
            "is_staff_view": False,
        }
        return render(request, self.template_name, context)



class StaffBoyProfileView(LoginRequiredMixin, StaffOnlyMixin, View):
    template_name = "boy/profile.html"   # reuse same template

    def get(self, request, pk):
        boy = get_object_or_404(CustomUser, pk=pk, is_boy_user=True)

        form = BoyProfileForm(instance=boy)

        # Disable all fields for staff (read-only)
        for field in form.fields.values():
            field.disabled = True

        registrations = Registration.objects.filter(boy=boy).select_related("event").order_by("-registration_date")
        payments = Payment.objects.filter(registration__boy=boy).select_related("registration__event").order_by("-paid_at")
        total_earnings = payments.filter(payment_status="Paid").aggregate(
            total=models.Sum("amount")
        )["total"] or 0

        context = {
            "form": form,
            "target_user": boy,
            "registrations": registrations,
            "payments": payments,
            "total_earnings": total_earnings,
            "is_staff_view": True,   # staff viewing boy
        }
        return render(request, self.template_name, context)

