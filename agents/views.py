from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Agent, GlobalWhatsApp, Post, Category


def agents_table_view(request):
    agent_type = request.GET.get('type', '').strip()
    recent_posts = Post.objects.order_by('-created_at')[:5]  # ✅ add this
    agent_id = request.GET.get('agent_id', '').strip()
    agents = Agent.objects.all().order_by('display_id')

    if agent_type:
        agents = agents.filter(type_label__icontains=agent_type)
    if agent_id:
        agents = agents.filter(display_id__icontains=agent_id)

    gw = GlobalWhatsApp.objects.first()
    numbers = gw.get_numbers_list() if gw else []

    for i, a in enumerate(agents):
        if numbers:
            a.whatsapp_number = numbers[i % len(numbers)]
            a.whatsapp_link = f"https://wa.me/{a.whatsapp_number}"
        else:
            a.whatsapp_number = ""
            a.whatsapp_link = "#"

    # ✅ ADD THIS
    recent_posts = Post.objects.order_by('-created_at')[:5]
    categories = Category.objects.all()

    return render(request, "agents_table_with_search.html", {
        "agents": agents,
        "filter_type": agent_type,
        "filter_agent_id": agent_id,
        "recent_posts": recent_posts,  # ✅ Now sidebar will work
        "categories": categories,      # ✅ Add categories also
    })



def blog_list(request, slug=None):
    posts_qs = Post.objects.all().order_by('-created_at')

    if slug:
        posts_qs = posts_qs.filter(category__slug=slug)

    search_query = request.GET.get('q')
    if search_query:
        posts_qs = posts_qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    return render(request, "blog_list.html", {
        "posts": posts_page,
        "recent_posts": Post.objects.order_by('-created_at')[:5],
        "categories": Category.objects.all(),
        "current_category": slug,
        "search_query": search_query,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, "post_detail.html", {"post": post})



def about_page(request):
    return render(request, "pages/about.html")

def contact_page(request):
    return render(request, "pages/contact.html")

def privacy_policy_page(request):
    return render(request, "pages/privacy_policy.html")
def terms_page(request):
    return render(request, "pages/terms.html")
