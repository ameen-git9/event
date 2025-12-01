from django.contrib import admin
from django.urls import path
from event_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # -----------------------
    # Landing + Auth
    # -----------------------
    path('admin/', admin.site.urls),


    path("", views.LandingPageView.as_view(), name="landing_page"),

    path("staff-login/", views.StaffLoginView.as_view(), name="staff_login"),
    path("boy-login/", views.BoyLoginView.as_view(), name="boy_login"),
    path("set-password/<int:user_id>/", views.SetPasswordView.as_view(), name="set_password"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    # -----------------------
    # Staff Dashboard
    # -----------------------
    path("staff/dashboard/", views.StaffDashboardView.as_view(), name="staff_dashboard"),

    # -----------------------
    # Staff → Manage Boys
    # -----------------------
    path("staff/add-boy/", views.AddBoyView.as_view(), name="add_boy"),
    path("staff/boys/", views.BoysListView.as_view(), name="view_boys"),
    path("staff/boys/<int:pk>/edit/", views.EditBoyView.as_view(), name="edit_boy"),

    # NEW: Staff view boy profile
    path("staff/boys/<int:pk>/profile/", views.StaffBoyProfileView.as_view(), name="staff_boy_profile"),

    # -----------------------
    # Staff → Manage Events
    # -----------------------
    path("staff/events/create/", views.CreateEventView.as_view(), name="create_event"),

    # -----------------------
    # Events (visible to both staff & boys)
    # -----------------------
    path("events/", views.EventsListView.as_view(), name="view_events"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("events/<int:pk>/edit/", views.EditEventView.as_view(), name="edit_event"),
    path("events/<int:pk>/delete/", views.DeleteEventView.as_view(), name="delete_event"),

    # -----------------------
    # Event Registration (Boy only)
    # -----------------------
    path("events/<int:pk>/register/", views.RegisterForEventView.as_view(), name="register_event"),

    # -----------------------
    # Boy Dashboard
    # -----------------------
    path("boy/dashboard/", views.BoyDashboardView.as_view(), name="boy_dashboard"),

    # Boy Profile (editable)
    path("boy/profile/", views.BoyProfileView.as_view(), name="boy_profile"),

    # -----------------------
    # Payments
    # -----------------------

    path("payments/history/", views.PaymentHistoryView.as_view(), name="payment_history"),
    path("payments/<int:payment_id>/simulate/", views.SimulatePaymentView.as_view(), name="simulate_payment"),
    path("payments/<int:payment_id>/razorpay-order/", views.CreateRazorpayOrderView.as_view(), name="create_order"),
    path("razorpay/callback/", views.RazorpayCallbackView.as_view(), name="razorpay_callback"),
    path("razorpay/failed/", views.RazorpayFailView.as_view(), name="razorpay_failed"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
