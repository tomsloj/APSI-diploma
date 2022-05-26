from django.shortcuts import render

from django.http import HttpRequest

from allauth.account.decorators import login_required

from .backend.creation import Creation
from .backend.user_manager import UserManager, StudentState, UserType

from .models import User, Paper


@login_required(login_url="/login")
def home_page(request: HttpRequest):

    UserManager.add_user(request.user.username)

    user_type = UserManager.get_user_type(request.user.username)

    if user_type == UserType.STUDENT:
        state = UserManager.get_student_state(request.user.username)

        if state == StudentState.ADD_TITLE:
            if request.method == "POST":
                creation = Creation(request.user.username)

                creation.create_theme(
                    request.POST["promoter_name"], request.POST["paper_title"]
                )
                UserManager.update_state(request.user.username)
                return render(request, "diploma_app/wait.html")
            return render(request, "diploma_app/create.html")
        elif state == StudentState.WAIT_FOR_TITLE_ACCEPT:
            return render(request, "diploma_app/wait.html")
        elif state == StudentState.SEND_PAPER:
            return render(request, "diploma_app/send.html")
        elif state == StudentState.WAIT_FOR_PAPER_ACCEPT:
            return render(request, "diploma_app/wait.html")
        return render(request, "diploma_app/home.html")
    elif user_type == UserType.PROMOTER:
        print("prace oczekujące na potwierdzenie")
        print(UserManager.get_pending_titles(request.user.username))

        if request.method == "POST":
            student_username = request.POST["username"]
            title = request.POST["paper_title"]
            accept = request.POST["accept_text"]

            if accept == "tak":
                UserManager.accept_title(student_username, title)
            else:
                UserManager.discard_title(student_username, title)

            creation.create_theme(
                request.POST["promoter_name"], request.POST["paper_title"]
            )
            UserManager.update_state(request.user.username)
            return render(request, "diploma_app/wait.html")

        return render(request, "diploma_app/accept_title.html")
