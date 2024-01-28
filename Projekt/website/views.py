from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from .models import Transaction
from .models import Category
from . import db
import json
from sqlalchemy.sql import func
import locale

views = Blueprint('views', __name__)



locale.setlocale(locale.LC_ALL, 'sk_SR') 


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    name = current_user.first_name

    income =  db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.type == "príjem", Transaction.user_id==current_user.id).first()

    print(income[0])
   
    if income[0] is None:
        income = 0.00
    else:
        income = income[0]

    totalIncome = (locale.format_string('%.2f', income, True))
    
    
    expense = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.type == "výdaj", Transaction.user_id==current_user.id).first() 
    print(expense[0])
    
    if expense[0] is None:
        expense = 0.00
    else:
        expense = expense[0]

    totalExpense = (locale.format_string('%.2f', expense, True))
    
    balance = income-expense
   
   
    formattedBalance = (locale.format_string('%.2f', balance, True))


    #tu menime 
    income_vs_expense = db.session.query(db.func.sum(Transaction.amount), Transaction.type).group_by(Transaction.type).order_by(Transaction.type).filter(Transaction.user_id == current_user.id).all()

    category_comparison = db.session.query(db.func.sum(Transaction.amount), Transaction.category).group_by(Transaction.category).order_by(Transaction.category).filter(Transaction.user_id == current_user.id, Transaction.type == 'príjem').all()

    vydaje_udaje = db.session.query(db.func.sum(Transaction.amount), Transaction.category).group_by(Transaction.category).order_by(Transaction.category).filter(Transaction.user_id == current_user.id, Transaction.type == 'výdaj').all()

    dates = db.session.query(db.func.sum(Transaction.amount), Transaction.date).group_by(Transaction.date).order_by(Transaction.date).filter(Transaction.user_id == current_user.id).all()

    

    income_category = []
    cats_labels = []
    for amounts, category in  category_comparison:
        income_category.append(amounts)
        cats_labels.append(category)


    expense_category = []
    expense_cats_labels = []
    for amounts, category in  vydaje_udaje:
        expense_category.append(amounts)
        expense_cats_labels.append(category)


    
    income_expense = []
    prijem_vydaj_labels = []
    for total_amount, label in income_vs_expense:
        income_expense.append(total_amount)
        prijem_vydaj_labels.append(label)

    over_time_expenditure = []
    dates_label = []
    for amount, date in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(amount)

                        
    
    return render_template("home.html", text=name, user=current_user, totalIncome=totalIncome, totalExpense=totalExpense, balance=formattedBalance,
    income_vs_expense=json.dumps(income_expense),
                            prijem_vydaj_labels=json.dumps( prijem_vydaj_labels),
                            income_category=json.dumps(income_category),
                            cats_labels = json.dumps(cats_labels),
                            over_time_expenditure=json.dumps(over_time_expenditure),
                            dates_label =json.dumps(dates_label),

                            
                            expense_category = json.dumps(expense_category),

                            expense_cats_labels = json.dumps(expense_cats_labels)

    
    )






@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            
            

    return jsonify({})





@views.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():  
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Názov je príliš krátky!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
           
        
        
            

    return render_template("wishlist.html", user=current_user)





@views.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions(): 
    entries = Transaction.query.order_by(Transaction.date.desc()).filter(Transaction.user_id == current_user.id).all()
    return render_template("transactions.html", user=current_user, entries=entries)



@views.route('/categories', methods=['GET', 'POST'])
@login_required
def categories(): 
    entries = Category.query.order_by(Category.id.desc()).filter(Category.user_id == current_user.id).all()
    return render_template("categories.html", user=current_user, entries=entries)






@views.route("/addCategory", methods=["GET", "POST"])
def addCategory():
   
    if request.method == 'POST':
        name = request.form['name']
       

        str = request.form['icon']
        arr = str.split("|")
        icon = arr[0]
        type = arr[1]
        user_id = current_user.id

      
    
        entry = Category(type, name, icon, user_id)
        db.session.add(entry)
        db.session.commit()
      
        flash("Kategória bola pridaná",'success')
        return redirect(url_for('views.categories'))
    return render_template('addCategory.html',user=current_user)





@views.route('/deleteCategory/<int:id>')
def deleteCategory(id):
    row = Category.query.get_or_404(int(id))
    db.session.delete(row)
    db.session.commit()
 
   
    flash('Kategória bola vymazaná.', 'success close')
    return redirect(url_for('views.categories'))





@views.route("/addTransaction", methods=["GET", "POST"])
def addTransaction():
    
    categories = Category.query.order_by(Category.id.desc()).filter(Category.user_id == current_user.id).all()
    
    if request.method == 'POST':   
        
        str = request.form['icon']
        arr = str.split("|")
        category = arr[0]
        type = arr[1]
        user_id = current_user.id

      
        amount = request.form['amount']
        
       
        
        entry = Transaction(type, category, amount, user_id)
        db.session.add(entry)
        db.session.commit()
     
        flash("Transakcia bola pridaná",'success')
        return redirect(url_for('views.transactions'))
    return render_template('addTransaction.html',user=current_user, categories=categories)
    







@views.route("/editTransaction/<int:id>", methods=["GET", "POST"])
def editTransaction(id):  
    transaction = Transaction.query.get_or_404(id)
    categories = Category.query.order_by(Category.id.desc()).filter(Category.user_id == current_user.id).all()
    if request.method == 'POST':
        transaction.amount = request.form['amount']
        str= request.form['icon']
        arr = str.split("|")
        transaction.category=arr[0]
        transaction.type=arr[1]
        try:
            db.session.commit() 
            flash("Transakcia bola upravená",'success')
            return redirect('/transactions')
        except:
            return "Nepodarilo sa editovať transakciu"
    else:
        return render_template('editTransaction.html', transaction = transaction, categories=categories)
                    
                    

   




@views.route('/delete/<int:id>')
def delete(id):
    row = Transaction.query.get_or_404(int(id))
    db.session.delete(row)
    db.session.commit()
 
   
    flash('Položka bola vymazaná.', 'success close')
    return redirect(url_for('views.transactions'))




@views.route("/charts", methods=["GET", "POST"])
def charts():
  
    income_vs_expense = db.session.query(db.func.sum(Transaction.amount), Transaction.type).group_by(Transaction.type).order_by(Transaction.type).filter(Transaction.user_id == current_user.id).all()

    category_comparison = db.session.query(db.func.sum(Transaction.amount), Transaction.category).group_by(Transaction.category).order_by(Transaction.category).filter(Transaction.user_id == current_user.id, Transaction.type == 'príjem').all()

    vydaje_udaje = db.session.query(db.func.sum(Transaction.amount), Transaction.category).group_by(Transaction.category).order_by(Transaction.category).filter(Transaction.user_id == current_user.id, Transaction.type == 'výdaj').all()

    dates = db.session.query(db.func.sum(Transaction.amount), Transaction.date).group_by(Transaction.date).order_by(Transaction.date).filter(Transaction.user_id == current_user.id).all()

    entries = Transaction.query.order_by(Transaction.date.desc()).filter(Transaction.user_id == current_user.id).all()
    


    income_category = []
    cats_labels = []
    for amounts, category in  category_comparison:
        income_category.append(amounts)
        cats_labels.append(category)


    expense_category = []
    expense_cats_labels = []
    for amounts, category in  vydaje_udaje:
        expense_category.append(amounts)
        expense_cats_labels.append(category)


    
    income_expense = []
    prijem_vydaj_labels = []
    for total_amount, label in income_vs_expense:
        income_expense.append(total_amount)
        prijem_vydaj_labels.append(label)

    over_time_expenditure = []
    dates_label = []
    for amount, date in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(amount)
        
    return render_template('charts.html',user=current_user, entries=entries,
    income_vs_expense=json.dumps(income_expense),
                            prijem_vydaj_labels=json.dumps( prijem_vydaj_labels),
                            income_category=json.dumps(income_category),
                            cats_labels = json.dumps(cats_labels),
                            over_time_expenditure=json.dumps(over_time_expenditure),
                            dates_label =json.dumps(dates_label),

                            
                            expense_category = json.dumps(expense_category),

                            expense_cats_labels = json.dumps(expense_cats_labels))

                        

  