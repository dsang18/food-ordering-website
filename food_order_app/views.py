from django.shortcuts import render, redirect
from django.db import connection

def homepage(request):
    return render(request, "homepage.html")

def login(request):
    message = ""
    user_id = []
    if request.method=="POST":
        cursor = connection.cursor()
        phoneno = request.POST.get("phoneno",'')
        password = request.POST.get("passwd",'')
        cursor.execute("select uid, phone, password from authenticate where phone=%s;",[phoneno])
        try:
            user_id = list(cursor.fetchone())
        except TypeError:
            pass
        if not user_id:
                message = "No user with above credentials"
        elif user_id and password == user_id[2]:
            return redirect(f"/order-food/home/{user_id[0]}")
        else:
            if password!=user_id[2]:
                message = "incorrect password"
            
        cursor.close()
        connection.close()
    return render(request, "login page.html", {'message':message})


def register(request):
    message = ""
    user_id = []
    if request.method=="POST":
        cursor = connection.cursor()
        fullname = request.POST.get("name",'')
        emailid = request.POST.get("email",'')
        phoneno = request.POST.get("phone",'')
        password = request.POST.get("passwd",'')
        cursor.execute("select uid from authenticate where phone=%s",[phoneno])
        try:
            user_id = list(cursor.fetchone())
            message = "There is already a user with this phone number"    
        except TypeError:
            cursor.execute("insert into authenticate(fullname,emailid,phone,password) values(%s,%s,%s,%s)",[fullname, emailid, phoneno, password])
            return redirect("/order-food/login/")
        finally:
            cursor.close()
            connection.close()   

    return render(request, "signup.html", {'message':message}) 


def home(request, pk):
    return render(request, "home.html")


def veg_menu(request, pk):
    cursor = connection.cursor()
    cursor.execute("select * from menu where type='veg';")
    veg_menu = list(cursor.fetchall())
    if request.method=="POST":
        cursor = connection.cursor()
        food = request.POST.get("food",'')
        qty = request.POST.get("qty",'')
        index = [i for (i,a_tuple) in enumerate(veg_menu) if a_tuple[1]==food]
        perprice = veg_menu[index[0]][2]
        cursor.execute("insert into cart values(%s,%s,%s,%s,%s)", [pk, food, perprice, qty, perprice*int(qty)])
        return redirect(f"/order-food/home/{pk}/veg-menu/")
    cursor.close()
    connection.close() 
    return render(request, "veg.html", {"pk":pk, "veg_menu":veg_menu})


def nonveg_menu(request, pk):
    cursor = connection.cursor()
    cursor.execute("select * from menu where type='nonveg';")
    nonveg_menu = list(cursor.fetchall())
    if request.method=="POST":
        cursor = connection.cursor()
        food = request.POST.get("food",'')
        qty = request.POST.get("qty",'')
        index = [i for (i,a_tuple) in enumerate(nonveg_menu) if a_tuple[1]==food]
        perprice = nonveg_menu[index[0]][2]
        cursor.execute("insert into cart values(%s,%s,%s,%s,%s)", [pk, food, perprice, qty, perprice*int(qty)])
        return redirect(f"/order-food/home/{pk}/nonveg-menu/")
    cursor.close()
    connection.close() 
    return render(request, "nonveg.html", {"pk":pk, "nonveg_menu": nonveg_menu})
    


def my_profile(request, pk):
    cursor = connection.cursor()
    cursor.execute("select * from authenticate where uid=%s",[pk])
    profile_details = list(cursor.fetchall())
    cursor.close()
    connection.close()
    return render(request, "profile.html", {"pk":pk, "profile": profile_details[0]})


def cart(request, pk):
    cursor = connection.cursor()
    cursor.execute("select * from cart where uid=%s", [pk])
    cart_items = list(cursor.fetchall())
    total = 0
    for i in cart_items:
        total+=i[4]

    if request.method == "POST":
        for i in cart_items:
            if i[1] in request.POST:
                cursor.execute("delete from cart where fooditem=%s;",[i[1]])
                return redirect(f"/order-food/home/{pk}/cart/")
    cursor.close()
    connection.close()
    return render(request, "cart.html", {"pk":pk, "cart_items":cart_items, "total":total})
