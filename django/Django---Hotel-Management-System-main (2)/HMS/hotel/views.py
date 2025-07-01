from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User

from datetime import datetime, date, timedelta
import random
# Create your views here.
from accounts.models import *
from room.models import *
from hotel.models import *
from .forms import *
from .models import Bills # Đảm bảo đã import model Bills
from django.db.models import Sum # Import hàm Sum
from room.models import Booking, RoomServices # Import các model cần thiết
from django.utils import timezone

@login_required(login_url='login')
def home(request):
    # Lấy danh sách các nhóm của người dùng
    user_groups = request.user.groups.all()

    # Kiểm tra xem người dùng có thuộc nhóm nào không
    if user_groups.exists():
        role = str(user_groups[0]) # Lấy vai trò từ nhóm đầu tiên
        if role != "guest":
            return redirect("employee-profile", pk=request.user.id)
        else:
            return redirect("guest-profile", pk=request.user.id)
    else:
        # Xử lý cho trường hợp người dùng không thuộc nhóm nào
        # (ví dụ: superuser)
        # Có thể chuyển hướng họ đến trang admin hoặc một trang mặc định nào đó
        if request.user.is_superuser:
            return redirect('/admin/') # Chuyển superuser đến trang admin
        else:
            # Nếu là người dùng thường mà không có vai trò, có thể báo lỗi hoặc chuyển về trang login
            messages.error(request, "Your account does not have an assigned role.")
            return redirect('logout') # Đăng xuất và yêu cầu đăng nhập lại


@login_required(login_url='login')
def events(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    events = Event.objects.all()

    # eventAttendees = EventAttendees.objects.filter(guest = request.user.guest, event = )

    attendedEvents = None
    if role == 'guest':
        attendedEvents = EventAttendees.objects.filter(
            guest=request.user.guest)

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("type") != ""):
                events = events.filter(
                    eventType__contains=request.POST.get("type"))

            if (request.POST.get("name") != ""):
                events = events.filter(
                    location__contains=request.POST.get("location"))

            if (request.POST.get("fd") != ""):
                events = events.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                events = events.filter(
                    endDate__lte=request.POST.get("ed"))

            context = {
                "role": role,
                "events": events,
                "type": request.POST.get("type"),
                "location": request.POST.get("location"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }
            return render(request, path + "events.html", context)

        if 'Save' in request.POST:
            n = request.POST.get('id-text')
            temp = EventAttendees.objects.get(id=request.POST.get('id-2'))
            temp.numberOfDependees = n
            temp.save()

        if 'attend' in request.POST:  # attend button clicked
            attendedEvents = EventAttendees.objects.filter(
                guest=request.user.guest)
            tempEvent = events.get(id=request.POST.get('id'))
            # print("query set**",attendedEvents)
            # print("**object***",tempEvent)
            # print(tempEvent in attendedEvents)
            check = False
            for t in attendedEvents:
                if t.event.id == tempEvent.id:
                    check = True
                    break
            if not check:  # event not in the query set
                a = EventAttendees(event=tempEvent, guest=request.user.guest)
                a.save()
                return redirect('events')  # refresh page

        elif 'remove' in request.POST:  # remove button clicked
            tempEvent = events.get(id=request.POST.get('id'))
            EventAttendees.objects.filter(
                event=tempEvent, guest=request.user.guest).delete()
            return redirect('events')  # refresh page

    context = {
        "role": role,
        'events': events,
        'attendedEvents': attendedEvents,
        "type": request.POST.get("type"),
        "location": request.POST.get("location"),
        "fd": request.POST.get("fd"),
        "ed": request.POST.get("ed")
    }
    return render(request, path + "events.html", context)


@login_required(login_url='login')
def createEvent(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    form = createEventForm()
    if request.method == "POST":
        form = createEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('events')

    context = {
        'form': form,
        "role": role
    }
    return render(request, path + "createEvent.html", context)


@login_required(login_url='login')
def deleteEvent(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    event = Event.objects.get(id=pk)
    if request.method == "POST":
        event.delete()
        return redirect('events')

    context = {
        "role": role,
        'event': event

    }
    return render(request, path + "deleteEvent.html", context)


@ login_required(login_url='login')
def event_profile(request, id):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    tempEvent = Event.objects.get(id=id)
    attendees = EventAttendees.objects.filter(event=tempEvent)

    context = {
        "role": role,
        "attendees": attendees,
        "event": tempEvent
    }
    return render(request, path + "event-profile.html", context)


@ login_required(login_url='login')
def event_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    event = Event.objects.get(id=pk)
    form1 = editEvent(instance=event)

    context = {
        "role": role,
        "event": event,
        "form": form1,
    }

    if request.method == "POST":
        form1 = editEvent(request.POST, instance=event)
        if form1.is_valid:
            form1.save()
            return redirect("events")

    return render(request, path + "event-edit.html", context)


@ login_required(login_url='login')
def announcements(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    announcements = Announcement.objects.all()
    context = {
        "role": role,
        'announcements': announcements
    }

    if request.method == "POST":
        if 'sendAnnouncement' in request.POST:  # send button clicked
            sender = request.user.employee

            announcement = Announcement(
                sender=sender, content=request.POST.get('textid'))

            announcement.save()
            return redirect('announcements')

        if "filter" in request.POST:
            if (request.POST.get("id") != ""):
                announcements = announcements.filter(
                    id__contains=request.POST.get("id"))

            if (request.POST.get("content") != ""):
                announcements = announcements.filter(
                    content__contains=request.POST.get("content"))

            if (request.POST.get("name") != ""):
                users = User.objects.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                employees = Employee.objects.filter(user__in=users)
                announcements = announcements.filter(sender__in=employees)

            if (request.POST.get("date") != ""):
                announcements = announcements.filter(
                    date=request.POST.get("date"))

        context = {
            "role": role,
            'announcements': announcements,
            "id": request.POST.get("id"),
            "name": request.POST.get("name"),
            "content": request.POST.get("content"),
            "date": request.POST.get("date")
        }
        return render(request, path + "announcements.html", context)

    return render(request, path + "announcements.html", context)


@login_required(login_url='login')
def deleteAnnouncement(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    announcement = Announcement.objects.get(id=pk)
    if request.method == "POST":
        announcement.delete()
        return redirect('announcements')

    context = {
        "role": role,
        'announcement': announcement

    }
    return render(request, path + "deleteAnnouncement.html", context)


@ login_required(login_url='login')
def storage(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    storage = Storage.objects.all()
    context = {
        "role": role,
        'storage': storage
    }
    if request.method == "POST":
        if 'add' in request.POST:
            item = Storage(itemName=request.POST.get("itemName"), itemType=request.POST.get(
                "itemType"), quantitiy=request.POST.get("quantitiy"))
            item.save()
            storage = Storage.objects.all()

        elif 'save' in request.POST:
            id = request.POST.get("id")
            storages = Storage.objects.get(id=id)
            storages.quantitiy = request.POST.get("quantitiy")
            storages.save()

        if "filter" in request.POST:
            if (request.POST.get("id") != ""):
                storage = storage.filter(
                    id__contains=request.POST.get("id"))

            if (request.POST.get("name") != ""):
                storage = storage.filter(
                    itemName__contains=request.POST.get("name"))

            if (request.POST.get("type") != ""):
                storage = storage.filter(
                    itemType__contains=request.POST.get("type"))

        context = {
            "role": role,
            "storage": storage,
            "id": request.POST.get("id"),
            "name": request.POST.get("name"),
            "type": request.POST.get("type"),
            "q": request.POST.get("q"),

        }
        return render(request, path + "storage.html", context)

    return render(request, path + "storage.html", context)


@login_required(login_url='login')
def deleteStorage(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    storage = Storage.objects.get(id=pk)
    if request.method == "POST":
        storage.delete()
        return redirect('storage')

    context = {
        "role": role,
        'storage': storage

    }
    return render(request, path + "deleteStorage.html", context)


@login_required(login_url='login')
def food_menu(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    print(request.POST)
    if request.method == "POST":
        if 'add' in request.POST:
            foodmenu = FoodMenu(menuItems=request.POST.get("menuItems"), startDate=request.POST.get(
                "startDate"), endDate=request.POST.get("endDate"))
            foodmenu.save()

    food_menu = FoodMenu.objects.all()
    context = {
        "role": role,
        'food_menu': food_menu
    }
    return render(request, path + "food-menu.html", context)


@login_required(login_url='login')
def deleteFoodMenu(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    food_menu = FoodMenu.objects.get(pk=pk)
    if request.method == "POST":
        food_menu.delete()
        return redirect('food-menu')

    context = {
        "role": role,
        'food_menu': food_menu

    }
    return render(request, path + "deleteFoodMenu.html", context)


@login_required(login_url='login')
def food_menu_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    print(request.POST)
    food_menu = FoodMenu.objects.get(pk=pk)
    form1 = editFoodMenu(request.POST, instance=food_menu)
    if request.method == "POST":
        if form1.is_valid():
            form1.save()
            return redirect("food-menu")

    context = {
        "role": role,
        'food_menu': food_menu
    }
    return render(request, path + "food-menu-edit.html", context)


@ login_required(login_url='login')
def error(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    context = {
        "role": role
    }
    return render(request, path + "error.html", context)


# @login_required(login_url='login')
# def payment(request):
#     # role = str(request.user.groups.all()[0])
#     # path = role

#     # # create random string:
#     # # generating the random code to be sent to the email
#     # import random
#     # import string
#     # code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase)
#     #                for _ in range(10))

#     # context = {
#     #     "role": role,
#     #     "code": code

#     # }

#     # def send(request, receiver, code):
#     #     subject = "Payment Verification"
#     #     text = """ 
#     #         Dear {guestName},
#     #         Please Copy Paste This Code in the verification Window:

#     #         {code}

#     #         Please ignore this email, if you didn't initiate this transaction!
#     #     """
#     #     # placing the code and user name in the email bogy text
#     #     email_text = text.format(
#     #         guestName=receiver.user.first_name + " " + receiver.user.last_name, code=code)

#     #     # seting up the email
#     #     message_email = 'hms@support.com'
#     #     message = email_text
#     #     receiver_name = receiver.user.first_name + " " + receiver.user.last_name

#     #     # send email
#     #     send_mail(
#     #         receiver_name + " " + subject,  # subject
#     #         message,  # message
#     #         message_email,  # from email
#     #         [receiver.user.email],  # to email
#     #         fail_silently=False,  # for user in users :
#     #         # user.email
#     #     )

#     #     messages.success(
#     #         request, 'Verification email Was Successfully Sent')

#     #     # do something ???
#     #     return render(request, path + "/verify.html", context)
#     # if role == "guest":
#     #     send(request, request.user.guest, code)
#     # elif role == "receptionist":
#     #     send(request, Booking.objects.all().last().guest, code)

#     # return render(request, path + "/payment.html", context)


# @login_required(login_url='login')
# def verify(request):
#     role = str(request.user.groups.all()[0])
#     path = role + "/"
#     if request.method == "POST":
#         tempCode = request.POST.get("tempCode")
#         if "verify" in request.POST:
#             realCode = request.POST.get("realCode")

#             if realCode == tempCode:
#                 messages.success(request, "Successful Booking")
#             else:
#                 Booking.objects.all().last().delete()
#                 messages.warning(request, "Invalid Code")

#             return redirect("rooms")
#     context = {
#         "role": role,
#         "code": tempCode

#     }
#     return render(request, path + "verify.html", context)
@login_required(login_url='login')
def payment(request):
    role = str(request.user.groups.all()[0])
    # path = role # Biến path có vẻ không được sử dụng để render, có thể bỏ

    # Bỏ phần tạo mã và gửi email
    # import random
    # import string
    # code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase)
    #                for _ in range(10))

    context = {
        "role": role,
        # "code": code # Không cần "code" nữa nếu không xác minh qua email
    }

    # Bỏ hoàn toàn hàm send và các lời gọi đến nó
    # def send(request, receiver, code):
    #     subject = "Payment Verification"
    #     text = """
    #         Dear {guestName},
    #         Please Copy Paste This Code in the verification Window:

    #         {code}

    #         Please ignore this email, if you didn't initiate this transaction!
    #     """
    #     email_text = text.format(
    #         guestName=receiver.user.first_name + " " + receiver.user.last_name, code=code)
    #     message_email = 'hms@support.com'
    #     message = email_text
    #     receiver_name = receiver.user.first_name + " " + receiver.user.last_name
    #     send_mail(
    #         receiver_name + " " + subject,
    #         message,
    #         message_email,
    #         [receiver.user.email],
    #         fail_silently=False,
    #     )
    #     messages.success(
    #         request, 'Verification email Was Successfully Sent')
    #     return render(request, path + "/verify.html", context) # Path này cũng cần xem lại

    # if role == "guest":
    #     # send(request, request.user.guest, code) # Bỏ lời gọi send
    #     pass # Hoặc xử lý logic khác nếu cần
    # elif role == "receptionist":
    #     # Giả sử logic lấy booking cuối cùng để gửi mail cho khách của booking đó
    #     # last_booking = Booking.objects.all().last()
    #     # if last_booking and last_booking.guest:
    #     #    send(request, last_booking.guest, code) # Bỏ lời gọi send
    #     # else:
    #     #    messages.warning(request, "Could not find a guest for the last booking to send verification.")
    #     pass # Hoặc xử lý logic khác nếu cần

    # Thay vì render verify.html từ hàm send, form payment.html sẽ trực tiếp submit đến verify URL
    # hoặc xử lý thanh toán trực tiếp tại đây nếu không cần bước xác minh riêng
    return render(request, role + "/payment.html", context)

@login_required(login_url='login')
def verify(request):
    role = str(request.user.groups.all()[0])
    # path = role + "/" # Biến path không được sử dụng để render

    if request.method == "POST":
        # Bỏ logic kiểm tra tempCode và realCode nếu không còn gửi email
        # tempCode = request.POST.get("tempCode")
        # if "verify" in request.POST: # Nút này có thể vẫn còn trên form verify.html
        #     realCode = request.POST.get("realCode")

        #     if realCode == tempCode:
        #         messages.success(request, "Successful Booking") # Hoặc "Payment Verified"
        #     else:
        #         # Nếu việc xác minh thất bại và bạn muốn xóa booking cuối cùng,
        #         # cần cẩn thận với logic này, đảm bảo nó đúng booking cần xóa.
        #         # last_booking = Booking.objects.all().last()
        #         # if last_booking:
        #         #    last_booking.delete()
        #         messages.warning(request, "Invalid Code / Verification Failed")

        #     return redirect("rooms") # Hoặc trang tóm tắt đơn hàng/thanh toán thành công

        # LOGIC MỚI: Nếu không còn xác minh qua email,
        # có thể bạn muốn xử lý thanh toán thành công luôn ở đây
        # hoặc đây là nơi xử lý callback từ cổng thanh toán (nếu có)
        # Hiện tại, nếu không có email, vai trò của trang "verify" này cần xem xét lại.
        # Giả sử sau khi người dùng nhấn "Pay" ở payment.html, họ được chuyển đến đây
        # và bạn muốn đánh dấu là thanh toán thành công.

        # Ví dụ: Cập nhật trạng thái booking là đã thanh toán (cần thêm trường status vào model Booking)
        # booking_to_update = Booking.objects.filter(guest=request.user.guest, status='pending_payment').last()
        # if booking_to_update:
        #    booking_to_update.status = 'paid'
        #    booking_to_update.save()
        #    messages.success(request, "Payment successful and booking confirmed!")
        # else:
        #    messages.warning(request, "No pending payment booking found to confirm.")

        # Vì không còn mã xác minh, chúng ta có thể mặc định là thành công
        # hoặc thêm logic kiểm tra khác nếu cần.
        messages.success(request, "Payment processed successfully!") # Thông báo chung
        return redirect("rooms") # Chuyển hướng sau khi "xác minh" (giờ là xử lý)

    # Nếu không phải POST hoặc không có logic xử lý cụ thể cho GET ở verify
    # có thể redirect người dùng hoặc hiển thị một trang đơn giản.
    # Truyền context rỗng hoặc context cần thiết nếu template verify.html vẫn được dùng.
    context = {
        "role": role,
        # "code": tempCode # Không còn code nữa
    }
    # Template verify.html có thể không cần thiết nữa nếu không có bước nhập mã.
    # Cân nhắc việc redirect trực tiếp từ payment đến trang thành công/thất bại.
    return render(request, role + "/verify.html", context)

@login_required(login_url='login')
def guest_report(request):
    # Chỉ cho phép vai trò 'guest' truy cập
    role = str(request.user.groups.all()[0])
    if role != 'guest':
        messages.error(request, "This page is only for guests.")
        return redirect('home')

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # Tạo một đối tượng Report nhưng chưa lưu ngay vào DB
            report_instance = form.save(commit=False)
            # Gán ngày tạo là ngày hiện tại
            report_instance.createdDate = timezone.now().date()
            # Lưu đối tượng vào DB
            report_instance.save()
            
            messages.success(request, "Thank you! Your report has been sent successfully.")
            return redirect('home') # Chuyển hướng về trang chủ sau khi gửi thành công
    else:
        # Nếu là GET request, chỉ hiển thị form trống
        form = ReportForm()

    context = {
        'role': role,
        'form': form
    }
    return render(request, 'guest/send_report.html', context)

def view_reports(request):
    # Chỉ cho phép vai trò 'admin' hoặc 'manager' truy cập
    role = str(request.user.groups.all()[0])
    if role not in ['admin', 'manager']:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # Lấy tất cả các report, sắp xếp theo ngày mới nhất ở trên
    all_reports = Report.objects.all().order_by('-date')

    context = {
        'role': role,
        'reports': all_reports
    }
    
    # Giả sử cả admin và manager đều dùng chung một template trong thư mục manager
    return render(request, 'manager/view_reports.html', context)

@login_required(login_url='login')
def revenue_report(request):
    # --- KIỂM TRA QUYỀN TRUY CẬP ---
    user_groups = request.user.groups.all()
    if not user_groups.exists():
        if request.user.is_superuser:
            return redirect('/admin/')
        else:
            messages.error(request, "Your account does not have an assigned role.")
            return redirect('logout')
            
    role = str(user_groups[0])
    if role not in ['admin', 'manager']:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    # --- BƯỚC 1: TÍNH TOÁN VÀ CẬP NHẬT HÓA ĐƠN CHO TẤT CẢ KHÁCH HÀNG ---
    all_guests = Guest.objects.all()
    for guest in all_guests:
        guest_bookings = Booking.objects.filter(guest=guest)
        
        # Tính doanh thu phòng cho khách này (cách an toàn)
        guest_room_revenue = 0
        for booking in guest_bookings:
            if booking.endDate and booking.startDate:
                num_nights = (booking.endDate - booking.startDate).days
                if num_nights > 0:
                    guest_room_revenue += num_nights * booking.roomNumber.price

        # Tính doanh thu dịch vụ cho khách này
        service_revenue_data = RoomServices.objects.filter(curBooking__in=guest_bookings).aggregate(total=Sum('price'))
        guest_service_revenue = service_revenue_data.get('total') or 0

        # Tổng doanh thu của khách
        guest_total_amount = guest_room_revenue + guest_service_revenue

        # Chỉ tạo hoặc cập nhật hóa đơn nếu có doanh thu
        if guest_total_amount > 0:
            Bills.objects.update_or_create(
                guest=guest,
                defaults={'totalAmount': guest_total_amount, 'date': timezone.now().date()}
            )
        # Nếu khách không có doanh thu, có thể xóa hóa đơn cũ (tùy chọn)
        # else:
        #     Bills.objects.filter(guest=guest).delete()


    # --- BƯỚC 2: LẤY TOÀN BỘ DỮ LIỆU ĐỂ HIỂN THỊ BÁO CÁO ---
    # Lấy tất cả các booking và room service để hiển thị chi tiết
    all_bookings = Booking.objects.all().order_by('-startDate')
    all_room_services = RoomServices.objects.all().order_by('-createdDate')
    
    # Lấy tất cả các hóa đơn đã được cập nhật từ BƯỚC 1
    all_bills = Bills.objects.all().order_by('-totalAmount')

    # --- BƯỚC 3: TÍNH CÁC SỐ TỔNG HỢP ĐỂ HIỂN THỊ ---
    # Tính lại tổng doanh thu phòng và dịch vụ từ dữ liệu gốc để hiển thị
    total_room_revenue_display = 0
    for booking in all_bookings:
        if booking.endDate and booking.startDate:
            num_nights = (booking.endDate - booking.startDate).days
            if num_nights > 0:
                total_room_revenue_display += num_nights * booking.roomNumber.price
    
    total_service_revenue_display = (all_room_services.aggregate(total=Sum('price'))['total'] or 0)
    
    grand_total_revenue_display = total_room_revenue_display + total_service_revenue_display

    # --- BƯỚC 4: GỬI DỮ LIỆU TỚI TEMPLATE ---
    context = {
        'role': role,
        'total_room_revenue': total_room_revenue_display,
        'total_service_revenue': total_service_revenue_display,
        'grand_total_revenue': grand_total_revenue_display,
        'all_bookings': all_bookings,
        'all_room_services': all_room_services,
        'all_bills': all_bills,
    }
    
    return render(request, 'manager/revenue_report.html', context)