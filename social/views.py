from django.shortcuts import render,redirect
from django.views.generic import View,CreateView,FormView,TemplateView,UpdateView,DeleteView,ListView
from django.contrib.auth.models import User
from social.forms import RegistrationForm,SignInForm,UserProfileForm,PostForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from social.models import UserProfile,Posts,Comments
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache




# Create your views here.

def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect('signin')
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[signin_required,never_cache]

class RegistrationView(CreateView):
    model=User
    form_class=RegistrationForm
    template_name='register.html'
    success_url=reverse_lazy('signin')

class SignInView(FormView):
    form_class=SignInForm
    template_name='signin.html'

    def post(self,request,*args,**kwargs):
        form=SignInForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get('username')
            pwd=form.cleaned_data.get('password')
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                return redirect('home')
            else:
                return render(request,self.template_name,{'form':form})

@signin_required
@never_cache
def signout_view(request,*args,**kwargs):
    logout(request)
    return redirect('signin')

@method_decorator(decs,name='dispatch')
class IndexView(CreateView,ListView):
    model=Posts
    form_class=PostForm
    template_name='home.html'
    success_url=reverse_lazy('home')
    context_object_name='posts'

    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return Posts.objects.all().order_by('-created_date')
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        userprofiles=UserProfile.objects.all()
        lst=[]
        for pro in userprofiles:
            for u in pro.followings.all():
                lst.append(u)
        print('follower count is',lst.count(self.request.user))
        context['fwsc']=lst.count(self.request.user)
        return context
    
@method_decorator(decs,name='dispatch')
class ProfileCreateView(CreateView):
    form_class=UserProfileForm
    template_name='profile-add.html'
    success_url=reverse_lazy('home')

    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)

@method_decorator(decs,name='dispatch')
class ProfileDetailView(TemplateView):
    template_name='profile-detail.html'

@method_decorator(decs,name='dispatch')
class ProfileEditView(UpdateView):
    model=UserProfile
    form_class=UserProfileForm
    template_name='profile-edit.html'
    success_url=reverse_lazy('profile-detail')

@method_decorator(decs,name='dispatch')
class AddCommentView(View):
    def post(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        pst=Posts.objects.get(id=id)
        usr=request.user
        cmnt=request.POST.get('comment')
        Comments.objects.create(user=usr,post=pst,comment=cmnt)
        return redirect('home')

@method_decorator(decs,name='dispatch')
class AddLikeView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        pst=Posts.objects.get(id=id)
        pst.liked_by.add(request.user)
        pst.save()
        return redirect('home')
    
def following_view(request,*args,**kwargs):
    id=kwargs.get('pk')
    usr=User.objects.get(id=id)
    request.user.profile.followings.add(usr)
    return redirect('home')



