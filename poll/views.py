from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponseRedirect
from .forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import Candidate, ControlVote, Position
from .forms import ChangeForm

def homeView(request):
    return render(request, "poll/home.html")


def registrationView(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            if cd['password'] == cd['confirm_password']:
                obj = form.save(commit=False)
                obj.set_password(obj.password)
                obj.save()
                messages.success(request, 'You have been registered.')
                return redirect('home')

            else:
                return render(request, "poll/registration.html", {'form':form,'note':'password must match'})

    else:
        form = RegistrationForm()

    return render(request, "poll/registration.html", {'form':form})


def loginView(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('dashboard')

        else:
            messages.success(request, 'Invalid username or password!')
            return render(request, "poll/login.html")

    else:
        return render(request, "poll/login.html")


@login_required
def logoutView(request):
    logout(request)
    return redirect('home')


@login_required
def dashboardView(request):
    return render(request, "poll/dashboard.html")


@login_required
def positionView(request):
    user_votes = ControlVote.objects.filter(user=request.user)
    positions = set(Position.objects.all())
    voted_positions = set(p.position for p in user_votes)
    not_voted_positions = list(positions - voted_positions)

    context = {'positions': not_voted_positions,
               'candidates': [p.candidate for p in user_votes]}

    return render(request, "poll/position.html", context)


@login_required
def candidateView(request, pk_position):
    position = get_object_or_404(Position, pk=pk_position)

    if request.method == "POST":

        user = request.user
        control_vote = ControlVote.objects.get_or_create(
            user=user, position=position)[0]

        if control_vote.status == False:
            candidate = Candidate.objects.get(pk=request.POST.get(position.title))
            candidate.total_vote += 1
            candidate.save()

            control_vote.status = True
            control_vote.candidate = candidate
            control_vote.save()

            return HttpResponseRedirect('/position/')

        else:
            messages.success(request, 'you have already been voted this position.')
            return render(request, 'poll/candidate.html', {'position': position})

    else:
        return render(request, 'poll/candidate.html', {'position': position})


@login_required
def resultView(request):
    candidates = Candidate.objects.all().order_by('position','-total_vote')
    return render(request, "poll/result.html", {'candidates': candidates})


@login_required
def candidateDetailView(request, pk_candidate):
    candidate = get_object_or_404(Candidate, pk=pk_candidate)
    return render(request, "poll/candidate_detail.html", {'candidate': candidate})


@login_required
def changePasswordView(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            return redirect('dashboard')

    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "poll/password.html", {'form': form})


@login_required
def editProfileView(request):
    if request.method == "POST":
        form = ChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = ChangeForm(instance=request.user)

    return render(request, "poll/edit_profile.html", {'form': form})
