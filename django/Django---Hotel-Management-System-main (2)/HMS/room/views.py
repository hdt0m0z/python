# imports
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



@ login_required(login_url='login')
def rooms(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    rooms = Room.objects.all()
    firstDayStr = None
    lastDateStr = None

    def chech_availability(fd, ed):
        availableRooms = []
        for room in rooms:
            availList = []
            bookingList = Booking.objects.filter(roomNumber=room)
            if room.statusStartDate == None:
                for booking in bookingList:
                    if booking.startDate > ed.date() or booking.endDate < fd.date():
                        availList.append(True)
                    else:
                        availList.append(False)
                if all(availList):
                    availableRooms.append(room)
            else:
                if room.statusStartDate > ed.date() or room.statusEndDate < fd.date():
                    for booking in bookingList:
                        if booking.startDate > ed.date() or booking.endDate < fd.date():
                            availList.append(True)
                        else:
                            availList.append(False)
                        if all(availList):
                            availableRooms.append(room)

        return availableRooms

    if request.method == "POST":
        if "dateFilter" in request.POST:
            firstDayStr = request.POST.get("fd", "")
            lastDateStr = request.POST.get("ld", "")

            firstDay = datetime.strptime(firstDayStr, '%Y-%m-%d')
            lastDate = datetime.strptime(lastDateStr, '%Y-%m-%d')

            rooms = chech_availability(firstDay, lastDate)

        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = rooms.filter(
                    number__contains=request.POST.get("number"))

            if (request.POST.get("capacity") != ""):
                rooms = rooms.filter(
                    capacity__gte=request.POST.get("capacity"))

            if (request.POST.get("nob") != ""):
                rooms = rooms.filter(
                    numberOfBeds__gte=request.POST.get("nob"))

            if (request.POST.get("type") != ""):
                rooms = rooms.filter(
                    roomType__contains=request.POST.get("type"))

            if (request.POST.get("price") != ""):
                rooms = rooms.filter(
                    price__lte=request.POST.get("price"))

            context = {
                "role": role,
                "rooms": rooms,
                "number": request.POST.get("number"),
                "capacity": request.POST.get("capacity"),
                "nob": request.POST.get("nob"),
                "price": request.POST.get("price"),
                "type": request.POST.get("type")
            }
            return render(request, path + "rooms.html", context)

    context = {
        "role": role,
        'rooms': rooms,
        'fd': firstDayStr,
        'ld': lastDateStr
    }
    return render(request, path + "rooms.html", context)


@login_required(login_url='login')
def add_room(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    if request.method == "POST":
        guest = None
        if role == 'guest':
            guest = request.user.guest
        elif role == 'manager' or role == 'admin' or role == 'receptionist':
            guest = request.user.employee

        # announcement = Announcement(sender = sender, content = request.POST.get('textid'))
        number = request.POST.get('number')
        capacity = request.POST.get('capacity')
        numberOfBeds = request.POST.get('beds')
        roomType = request.POST.get('type')
        price = request.POST.get('price')
        print(capacity)
        room = Room(number=number, capacity=capacity,
                    numberOfBeds=numberOfBeds, roomType=roomType, price=price)

        room.save()
        return redirect('rooms')

    context = {
        "role": role
    }
    return render(request, path + "add-room.html", context)


@login_required(login_url='login')
def room_profile(request, id):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    tempRoom = Room.objects.get(number=id)
    bookings = Booking.objects.filter(roomNumber=tempRoom)
    guests = Guest.objects.all()
    bookings2 = Booking.objects.all()
    context = {
        "role": role,
        "bookings": bookings,
        "room": tempRoom,
        "guests": guests,
        "bookings2": bookings2
    }

    if request.method == "POST":
        if "lockRoom" in request.POST:
            fd = request.POST.get("bsd")
            ed = request.POST.get("bed")
            fd = datetime.strptime(fd, '%Y-%m-%d')
            ed = datetime.strptime(ed, '%Y-%m-%d')
            check = True
            for b in bookings:
                if b.endDate >= fd.date() and b.startDate <= ed.date():
                    check = False
                    break
            if check:
                tempRoom.statusStartDate = fd
                tempRoom.statusEndDate = ed
                tempRoom.save()
            else:
                messages.error(request, "There is a booking in the interval!")
        if "unlockRoom" in request.POST:
            tempRoom.statusStartDate = None
            tempRoom.statusEndDate = None
            tempRoom.save()
        if "deleteRoom" in request.POST:
            check = True
            for b in bookings:
                if b.startDate <= datetime.now().date() or b.endDate >= datetime.now().date():
                    check = False
            if check:
                tempRoom.delete()
                return redirect("rooms")
            else:
                messages.error(request, "There is a booking in the interval!")

    return render(request, path + "room-profile.html", context)


@login_required(login_url='login')
def room_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room = Room.objects.get(number=pk)
    form1 = editRoom(instance=room)

    context = {
        "role": role,
        "room": room,
        "form1": form1
    }

    if request.method == 'POST':
        form1 = editRoom(request.POST, instance=room)
        if form1.is_valid():
            form1.save()
            return redirect("room-profile", id=room.number)
    return render(request, path + "room-edit.html", context)


@ login_required(login_url='login')
def room_services(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room_services = RoomServices.objects.all()
    context = {
        "role": role,
        "room_services": room_services
    }
    return render(request, path + "room-services.html", context)


@login_required(login_url='login')
def current_room_services(request):
    import datetime

    role = str(request.user.groups.all()[0])
    path = role + "/"

    curGuest = Guest.objects.get(user=request.user)
    curBooking = Booking.objects.filter(guest=curGuest).last()
    if curBooking is not None:
        curRoom = Room.objects.get(number=curBooking.roomNumber.number)
    else:
        context = {
            "role": role,
            "error": "You Don't Have Booking Right Now"
        }
        return render(request, path + "current-room-services.html", context)
    curRoomServices = RoomServices.objects.filter(curBooking=curBooking)

    room_services = RoomServices.objects.all()

    group = Group.objects.get(name='staff')
    users = User.objects.filter(groups=group)
    allEmployees = Employee.objects.filter(user__in=users)
    availableEmployee = list()
    maxTaskNum = 10

    for e in allEmployees:
        counter = 0
        empTasks = Task.objects.filter(employee=e)
        for t in empTasks:
            counter += 1
        if counter < maxTaskNum:
            availableEmployee.append(e)

    context = {
        "role": role,
        "room_services": room_services,
        "curGuest": curGuest,
        "curBooking": curBooking,
        "curRoom": curRoom,
        "curRoomServices": curRoomServices
    }

    if request.method == "POST":
        if "foodReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=50.0, room=curRoom,  servicesType='Food')
            newServiceReq.save()

            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()
            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Food Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Food Request")
            newTask.save()
            return redirect("current-room-services")

        if "cleaningReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=0.0, room=curRoom,  servicesType='Cleaning')
            newServiceReq.save()
            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()

            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Cleaning Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Cleaning Request")
            newTask.save()
            return redirect("current-room-services")

        if "techReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=0.0, room=curRoom,  servicesType='Technical')
            newServiceReq.save()
            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()
            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Tech Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Tech Request")
            newTask.save()
            return redirect("current-room-services")
        
        if "SpaReq" in request.POST:
            newServiceReq = RoomServices(
                curBooking=curBooking, price=30.0, room=curRoom,  servicesType='Spa')
            newServiceReq.save()
            chosenEmp = random.choice(availableEmployee)
            lastTask = Task.objects.filter(employee=chosenEmp).last()
            if(lastTask != None):
                newTask = Task(employee=chosenEmp, startTime=lastTask.endTime,
                               endTime=lastTask.endTime+datetime.timedelta(minutes=30), description="Spa Request")
            else:
                newTask = Task(employee=chosenEmp, startTime=datetime.datetime.now(),
                               endTime=datetime.datetime.now()+datetime.timedelta(minutes=30), description="Spa Request")
            newTask.save()
            return redirect("current-room-services")

    return render(request, path + "current-room-services.html", context)


@login_required(login_url='login')
def bookings(request):
    import datetime
    role = str(request.user.groups.all()[0])
    path = role + "/"

    bookings = Booking.objects.all()
    # calculating total for every booking:
    totals = {}  # <booking : total>
    for booking in bookings:
        start_date = datetime.datetime.strptime(
            str(booking.startDate), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(str(booking.endDate), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        price = Room.objects.get(number=booking.roomNumber.number).price
        total = price * numberOfDays
        totals[booking] = total

    if request.method == "POST":
        if "filter" in request.POST:
            if (request.POST.get("number") != ""):
                rooms = Room.objects.filter(
                    number__contains=request.POST.get("number"))
                bookings = bookings.filter(
                    roomNumber__in=rooms)

            if (request.POST.get("name") != ""):
                users = User.objects.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                guests = Guest.objects.filter(user__in=users)
                bookings = bookings.filter(
                    guest__in=guests)

            if (request.POST.get("rez") != ""):
                bookings = bookings.filter(
                    dateOfReservation=request.POST.get("rez"))

            if (request.POST.get("fd") != ""):
                bookings = bookings.filter(
                    startDate__gte=request.POST.get("fd"))

            if (request.POST.get("ed") != ""):
                bookings = bookings.filter(
                    endDate__lte=request.POST.get("ed"))

            context = {
                "role": role,
                'bookings': bookings,
                'totals': totals,
                "name": request.POST.get("name"),
                "number": request.POST.get("number"),
                "rez": request.POST.get("rez"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }

            return render(request, path + "bookings.html", context)

    context = {
        "role": role,
        'bookings': bookings,
        'totals': totals
    }
    return render(request, path + "bookings.html", context)


@login_required(login_url='login')
def booking_make(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    room = Room.objects.get(number=request.POST.get("roomid"))
    guests = Guest.objects.all()  # we pass this to context
    names = []
    if request.method == 'POST':
        if request.POST.get("fd") == "" or request.POST.get("ld") == "":
            return redirect("rooms")

        start_date = datetime.strptime(
            str(request.POST.get("fd")), "%Y-%m-%d")
        end_date = datetime.strptime(
            str(request.POST.get("ld")), "%Y-%m-%d")
        numberOfDays = abs((end_date-start_date).days)
        # get room peice:
        price = room.price
        total = price * numberOfDays

        if 'add' in request.POST:  # add dependee
            name = request.POST.get("depName")
            names.append(name)
            for i in range(room.capacity-2):
                nameid = "name" + str(i+1)
                if request.POST.get(nameid) != "":
                    names.append(request.POST.get(nameid))

        if 'bookGuestButton' in request.POST:
            if "guest" in request.POST:
                curguest = Guest.objects.get(id=request.POST.get("guest"))
            else:
                curguest = request.user.guest
            curbooking = Booking(guest=curguest, roomNumber=room, startDate=request.POST.get(
                "fd"), endDate=request.POST.get("ld"))
            curbooking.save()

            for i in range(room.capacity-1):
                nameid = "name" + str(i+1)
                if request.POST.get(nameid) != "":
                    if request.POST.get(nameid) != None:
                        d = Dependees(booking=curbooking,
                                      name=request.POST.get(nameid))
                        d.save()
            return redirect("payment")

    context = {
        "fd": request.POST.get("fd"),
        "ld": request.POST.get("ld"),
        "role": role,
        "guests": guests,
        "room": room,
        "total": total,
        "names": names
    }

    return render(request, path + "booking-make.html", context)


@login_required(login_url='login')
def deleteBooking(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    booking = Booking.objects.get(id=pk)
    if request.method == "POST":
        booking.delete()
        return redirect('bookings')

    context = {
        "role": role,
        'booking': booking

    }
    return render(request, path + "deleteBooking.html", context)


# @ login_required(login_url='login')
# def refunds(request):
#     role = str(request.user.groups.all()[0])
#     path = role + "/"

#     refunds = Refund.objects.all()
#     context = {
#         "role": role,
#         'refunds': refunds
#     }

#     if request.method == "POST":
#         if "decline" in request.POST or "approve" in request.POST:
#             refundId = request.POST.get("refund", "")
#             guestUserId = request.POST.get("guestUserId", "")

#             tempUser = User.objects.get(id=guestUserId)
#             receiver = Guest.objects.get(user=tempUser)

#             def send(request, receiver, text, subject):

#                 message_email = 'hms@support.com'
#                 message = text
#                 receiver_name = receiver.user.first_name + " " + receiver.user.last_name

#                 # send email
#                 send_mail(
#                     receiver_name + " " + subject,   # subject
#                     message,                          # message
#                     message_email,                    # from email
#                     [receiver.user.email],                    # to email
#                     fail_silently=False,              # for user in users :
#                     # user.email
#                 )

#                 messages.success(
#                     request, 'Feedback E-Mail Was Successfully Sent')

#                 Refund.objects.filter(id=refundId).delete()
#                 return render(request, path + "refunds.html", context)

#             def send_mail_refund_approved(request, receiver):
#                 subject = "Refund"
#                 text = """
#                     Dear {guestName},
#                     We are pleased to confirm that your refund request has been accepted.
#                     The amount of refund will be on your account in 24 hours.
#                     This time interval can change up to 48 hours according to your bank.
#                     We are very sorry for this inconvenience. We hope to see you soon.
#                 """
#                 email_text = text.format(
#                     guestName=receiver.user.first_name + " " + receiver.user.last_name)

#                 send(request, receiver, email_text, subject)

#             def send_mail_refund_declined(request, receiver):
#                 subject = "Refund"
#                 text = """
#                     Dear {guestName},
#                     We are sorry to inform you that your refund request has been declined.
#                     After our examinations, we see that your request can not be done according to our Hotel Policy.
#                     We are very sorry for this inconvenience. We hope to see you soon.
#                 """
#                 email_text = text.format(
#                     guestName=receiver.user.first_name + " " + receiver.user.last_name)

#                 send(request, receiver, email_text, subject)

#             if "decline" in request.POST:
#                 send_mail_refund_declined(request, receiver)
#             if "approve" in request.POST:
#                 send_mail_refund_approved(request, receiver)

#             refundId = None
#             statu = None

#         if "filter" in request.POST:
#             users = User.objects.all()
#             if (request.POST.get("gid") != ""):
#                 users = users.filter(
#                     id__contains=request.POST.get("gid"))
#                 guests = Guest.objects.filter(user__in=users)
#                 refunds = refunds.filter(guest__in=guests)

#             if (request.POST.get("name") != ""):
#                 users = users.filter(
#                     Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
#                 guests = Guest.objects.filter(user__in=users)
#                 refunds = refunds.filter(guest__in=guests)

#             if (request.POST.get("booking") != ""):
#                 booking = Booking.objects.get(id=request.POST.get("booking"))
#                 refunds = refunds.filter(reservation=booking)

#             if (request.POST.get("reason") != ""):
#                 refunds = refunds.filter(
#                     reason__contains=request.POST.get("reason"))

#             context = {
#                 "role": role,
#                 "refunds": refunds,
#                 "gid": request.POST.get("gid"),
#                 "name": request.POST.get("name"),
#                 "booking": request.POST.get("booking"),
#                 "reason": request.POST.get("reason")
#             }
#             return render(request, path + "refunds.html", context)

#     return render(request, path + "refunds.html", context)


# @login_required(login_url='login')
# def request_refund(request):
#     role = str(request.user.groups.all()[0])
#     path = role + "/"

#     curGuest = Guest.objects.get(user=request.user)

#     if request.method == "POST":
#         if "sendReq" in request.POST:
#             reason = request.POST.get("reqExp")
#             curBookingId = request.POST.get("bid")
#             currentBooking = Booking.objects.get(id=curBookingId)
#             temp = Refund.objects.filter(reservation=currentBooking)
#             if not temp:
#                 currentReq = Refund(
#                     guest=curGuest, reservation=currentBooking, reason=reason)
#                 currentReq.save()
#                 messages.success(
#                     request, "Your request was successfully sent.")
#             else:
#                 messages.error(
#                     request, "We already have your refund request for this reservation!")

#     context = {
#         "role": role,
#         "curGuest": curGuest,
#         "id": request.POST.get("bookingId")
#     }

#     return render(request, path + "request-refund.html", context)


@ login_required(login_url='login')
def refunds(request):
    role = str(request.user.groups.all()[0])
    path = role + "/" # Biến path này có thể không cần thiết nếu render trực tiếp với role

    refund_requests = Refund.objects.all() # Đổi tên biến refunds thành refund_requests để rõ ràng hơn

    if request.method == "POST":
        if "decline" in request.POST or "approve" in request.POST:
            refundId = request.POST.get("refund", "")
            # guestUserId = request.POST.get("guestUserId", "") # Không cần nữa nếu không gửi mail

            # tempUser = User.objects.get(id=guestUserId) # Không cần nữa
            # receiver = Guest.objects.get(user=tempUser) # Không cần nữa

            # --- BỎ HOÀN TOÀN KHỐI GỬI EMAIL ---
            # def send(request, receiver, text, subject):
            #     message_email = 'hms@support.com'
            #     message = text
            #     receiver_name = receiver.user.first_name + " " + receiver.user.last_name
            #     send_mail(
            #         receiver_name + " " + subject,
            #         message,
            #         message_email,
            #         [receiver.user.email],
            #         fail_silently=False,
            #     )
            #     messages.success(request, 'Feedback E-Mail Was Successfully Sent')
            #     # Không nên render ở đây, nên để logic chính xử lý sau khi send
            #     # Refund.objects.filter(id=refundId).delete() # Xóa refund nên làm ở ngoài hàm send
            #     # return render(request, path + "refunds.html", context) # Không return ở đây

            # def send_mail_refund_approved(request, receiver):
            #     # ... (nội dung hàm này bị bỏ) ...
            #     pass

            # def send_mail_refund_declined(request, receiver):
            #     # ... (nội dung hàm này bị bỏ) ...
            #     pass
            # --- KẾT THÚC KHỐI BỎ EMAIL ---

            action_taken = False
            if "approve" in request.POST:
                # send_mail_refund_approved(request, receiver) # Bỏ lời gọi
                # Thực hiện logic duyệt refund ở đây, ví dụ:
                try:
                    refund_to_approve = Refund.objects.get(id=refundId)
                    # Ví dụ: Cập nhật trạng thái của Booking liên quan đến refund này
                    # booking_to_update = refund_to_approve.reservation
                    # booking_to_update.status = 'refunded' # Giả sử có trường status
                    # booking_to_update.save()

                    # Sau đó xóa yêu cầu refund
                    refund_to_approve.delete()
                    messages.success(request, f"Refund request ID {refundId} approved and processed.")
                    action_taken = True
                except Refund.DoesNotExist:
                    messages.error(request, f"Refund request ID {refundId} not found.")

            elif "decline" in request.POST:
                # send_mail_refund_declined(request, receiver) # Bỏ lời gọi
                # Chỉ cần xóa yêu cầu refund nếu bị từ chối
                try:
                    refund_to_decline = Refund.objects.get(id=refundId)
                    refund_to_decline.delete()
                    messages.info(request, f"Refund request ID {refundId} declined.")
                    action_taken = True
                except Refund.DoesNotExist:
                    messages.error(request, f"Refund request ID {refundId} not found.")

            if action_taken:
                # Tải lại danh sách refund_requests sau khi xóa
                refund_requests = Refund.objects.all()
                # Không return ở đây để cho phép filter chạy nếu có
                # return redirect('refunds') # Hoặc redirect nếu không có filter

        # Logic filter vẫn giữ nguyên
        if "filter" in request.POST:
            # Lấy danh sách refund ban đầu cho mỗi lần filter để tránh filter chồng chéo sai
            filtered_refunds = Refund.objects.all()
            users_query = User.objects.all() # Queryset cho User để filter

            gid_filter = request.POST.get("gid")
            if gid_filter:
                # users_query = users_query.filter(id__contains=gid_filter) # Lọc User trước
                # guests_query = Guest.objects.filter(user__in=users_query)
                # filtered_refunds = filtered_refunds.filter(guest__in=guests_query)
                # Hoặc đơn giản hơn nếu gid là id của guest:
                filtered_refunds = filtered_refunds.filter(guest__user__id__contains=gid_filter)


            name_filter = request.POST.get("name")
            if name_filter:
                users_query_name = User.objects.filter(
                    Q(first_name__icontains=name_filter) | Q(last_name__icontains=name_filter)
                ) # Dùng icontains cho không phân biệt hoa thường
                guests_query_name = Guest.objects.filter(user__in=users_query_name)
                filtered_refunds = filtered_refunds.filter(guest__in=guests_query_name)

            booking_id_filter = request.POST.get("booking")
            if booking_id_filter:
                try:
                    # booking_instance = Booking.objects.get(id=booking_id_filter)
                    filtered_refunds = filtered_refunds.filter(reservation__id=booking_id_filter)
                except Booking.DoesNotExist:
                    # Nếu booking ID không tồn tại, có thể trả về danh sách rỗng hoặc bỏ qua filter này
                    filtered_refunds = filtered_refunds.none() 
                except ValueError: # Nếu booking_id_filter không phải số
                    messages.error(request, "Invalid Booking ID for filtering.")

            reason_filter = request.POST.get("reason")
            if reason_filter:
                filtered_refunds = filtered_refunds.filter(reason__icontains=reason_filter)

            context = {
                "role": role,
                "refunds": filtered_refunds, # Truyền danh sách đã filter
                "gid": gid_filter,
                "name": name_filter,
                "booking": booking_id_filter,
                "reason": reason_filter
            }
            return render(request, path + "refunds.html", context)

        # Nếu có action (approve/decline) và không có filter, cần redirect hoặc render lại
        # Để đơn giản, nếu có action, ta sẽ redirect để làm mới trang và message
        if action_taken:
            return redirect('refunds')

    # Nếu không phải POST hoặc không có action/filter cụ thể nào được xử lý ở trên
    # và đã có thay đổi refund_requests (ví dụ sau approve/decline không kèm filter)
    # cần đảm bảo refund_requests được cập nhật trước khi render.
    # Tuy nhiên, redirect ở trên đã xử lý việc này.

    context = {
        "role": role,
        'refunds': refund_requests # Danh sách refund ban đầu hoặc đã được cập nhật
    }
    return render(request, path + "refunds.html", context)

@login_required(login_url='login')
def request_refund(request):
    role = str(request.user.groups.all()[0])
    path = role + "/" # Biến path này có thể không cần nếu render trực tiếp

    # Lấy guest hiện tại, phải đảm bảo request.user là một guest
    # Nếu request.user có thể không phải là guest, cần xử lý lỗi
    try:
        curGuest = Guest.objects.get(user=request.user)
    except Guest.DoesNotExist:
        messages.error(request, "User profile not found or you are not logged in as a guest.")
        return redirect('home') # Hoặc một trang lỗi phù hợp

    booking_id_from_post = None
    if request.method == "POST":
        if "refReq" in request.POST: # Nút này đến từ guest-profile.html
            booking_id_from_post = request.POST.get("bookingId")
            # Lưu booking_id vào session để dùng ở GET request sau khi redirect
            request.session['refund_booking_id'] = booking_id_from_post
            # Redirect để tránh resubmit form nếu người dùng F5 trên trang request-refund
            # hoặc để đảm bảo trang request-refund luôn có bookingId đúng cách
            return redirect('request-refund') # Redirect đến chính nó (GET request)

        elif "sendReq" in request.POST: # Nút này đến từ form request-refund.html
            reason = request.POST.get("reqExp")
            curBookingId = request.POST.get("bid") # Lấy từ input hidden trong form

            if not curBookingId:
                messages.error(request, "Booking ID is missing. Cannot process refund request.")
                return redirect('guest-profile', pk=request.user.id) # Hoặc trang nào đó phù hợp

            try:
                currentBooking = Booking.objects.get(id=curBookingId, guest=curGuest)
                # Kiểm tra xem đã có yêu cầu refund cho booking này chưa
                if Refund.objects.filter(reservation=currentBooking, guest=curGuest).exists():
                    messages.error(request, "We already have your refund request for this reservation!")
                elif not reason:
                     messages.error(request, "Please provide a reason for your refund request.")
                else:
                    currentReq = Refund(
                        guest=curGuest,
                        reservation=currentBooking,
                        reason=reason
                    )
                    currentReq.save()
                    messages.success(request, "Your refund request was successfully sent.")
                    # Xóa booking_id khỏi session sau khi dùng
                    if 'refund_booking_id' in request.session:
                        del request.session['refund_booking_id']
                    return redirect('guest-profile', pk=request.user.id) # Chuyển về trang profile khách hàng
            except Booking.DoesNotExist:
                messages.error(request, "The specified booking does not exist or does not belong to you.")
                return redirect('guest-profile', pk=request.user.id)
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                # Không redirect ngay, để người dùng thấy form và lỗi (nếu template hiển thị lỗi form)
    
    # Xử lý cho GET request, hoặc sau khi POST không thành công và không redirect
    # Lấy booking_id từ session nếu có (sau khi redirect từ guest-profile)
    if request.method == "GET":
        booking_id_from_post = request.session.get('refund_booking_id')

    if not booking_id_from_post:
        # Nếu không có booking_id nào được truyền (ví dụ: truy cập trực tiếp URL)
        # hoặc session đã hết hạn/bị xóa
        messages.info(request, "Please select a booking from your profile to request a refund.")
        # Cân nhắc redirect về trang guest-profile nếu không có booking_id
        # return redirect('guest-profile', pk=request.user.id) # Hoặc không làm gì cả để template tự xử lý
        # Hiện tại, để template request-refund.html hiển thị, ta truyền id=None
        # Template cần kiểm tra xem id có giá trị không.
        pass


    context = {
        "role": role,
        "curGuest": curGuest, # Có thể không cần nếu template chỉ dùng request.user
        "id": booking_id_from_post # ID của booking cần refund
    }
    # Đảm bảo path + "request-refund.html" là đúng
    # Ví dụ: "guest/request-refund.html"
    return render(request, path + "request-refund.html", context)

@login_required(login_url='login')
def delete_room_service(request, pk):
    # Kiểm tra quyền, chỉ cho phép admin hoặc manager thực hiện
    role = str(request.user.groups.all()[0])
    if role not in ['manager', 'admin']:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('home')

    try:
        # Tìm đối tượng RoomService cần xóa dựa trên pk (primary key)
        service_to_delete = RoomServices.objects.get(id=pk)
        service_to_delete.delete()
        messages.success(request, f"Room service (ID: {pk}) has been successfully deleted.")
    except RoomServices.DoesNotExist:
        messages.error(request, "The requested room service does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")

    # Chuyển hướng người dùng về lại trang danh sách dịch vụ phòng
    return redirect('room-services')