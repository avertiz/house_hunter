import os
from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, Listing, Comment
from datetime import datetime
from flask_migrate import Migrate
from src import listing_metrics_config, get_address_from_url, calc_monthly_payment_est
from src import calc_av_model_score, calc_cost_score, calc_av_total_possible_score

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",  # Provided by Render for Postgres
    "sqlite:///db.sqlite3"  # Fallback for local dev
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if username:
            user = User.query.filter_by(name=username).first()
            if not user:
                user = User(name=username)
                db.session.add(user)
                db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('listings'))
    return render_template('login.html')

@app.route('/listings')
def listings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    all_listings = Listing.query.order_by(Listing.av_score.desc(), Listing.total_monthly_payment.desc()).all()
    col_groups = listing_metrics_config['col_group'].drop_duplicates().values.tolist()
    cols = { row['col']:[ row['col_group'],row['db.type'], row['display_name']  ] for _, row in listing_metrics_config.iterrows() }
    return render_template(
        'listings.html',
        listings=all_listings,
        col_groups=col_groups,
        cols=cols,
        av_model_score_total=calc_av_total_possible_score()
    )

@app.route('/add', methods=['GET', 'POST'])
def add_listing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        url = request.form['url']
        address = get_address_from_url(url=url)
        list_price = int(request.form['list_price'])
        annual_property_tax = int(request.form['annual_property_tax'])
        monthly_hoa = int(request.form['monthly_hoa'])

        cost_dict = calc_monthly_payment_est(
            annual_property_tax     = annual_property_tax,
            monthly_hoa             = monthly_hoa,
            loan_amount             = list_price * 0.9,
            annual_pmi              = list_price * 0.9 * .002,
            annual_interest_rate    =6,
            annual_insurance        =1500
        )

        cost_score = calc_cost_score(cost_dict=cost_dict)
        av_score = calc_av_model_score(form=request.form)

        new_listing = Listing(
            url=url,
            address=address,
            list_price=list_price,
            annual_property_tax=annual_property_tax,
            monthly_hoa=monthly_hoa,
            total_monthly_payment=cost_dict['total'],
            cost_score=cost_score,
            av_score=av_score
        )

        for _, row in listing_metrics_config.iterrows():
            key = row['col']
            if row['db.type'] == 'Integer':
                if request.form[key] == '':
                    value = None
                else:
                    value = int(request.form[key])
            elif row['db.type'] == 'Boolean':
                value = key in request.form
            else:
                value = None
            setattr(new_listing, key, value)
        db.session.add(new_listing)
        db.session.commit()
        return redirect(url_for('listings'))
    
    col_groups = listing_metrics_config['col_group'].drop_duplicates().values.tolist()
    cols = { row['col']:[ row['col_group'],row['db.type'], row['display_name']  ] for _, row in listing_metrics_config.iterrows() }

    return render_template('add_listing.html', col_groups=col_groups, cols=cols)

@app.route('/comment/<int:listing_id>', methods=['POST'])
def comment(listing_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    comment = Comment(user_id=session['user_id'], listing_id=listing_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('listings'))

@app.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
def edit_listing(listing_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    listing = Listing.query.get_or_404(listing_id)
    if request.method == 'POST':
        listing.url = request.form['url']
        listing.address = get_address_from_url(url=listing.url)

        list_price = int(request.form['list_price'])
        annual_property_tax = int(request.form['annual_property_tax'])
        monthly_hoa = int(request.form['monthly_hoa'])

        listing.list_price = list_price
        listing.annual_property_tax = annual_property_tax
        listing.monthly_hoa = monthly_hoa

        cost_dict = calc_monthly_payment_est(
            annual_property_tax     = annual_property_tax,
            monthly_hoa             = monthly_hoa,
            loan_amount             = list_price * 0.9,
            annual_pmi              = list_price * 0.9 * .002,
            annual_interest_rate    =6,
            annual_insurance        =1500
        )

        listing.cost_score = calc_cost_score(cost_dict=cost_dict)
        listing.av_score = calc_av_model_score(form=request.form)

        listing.total_monthly_payment = int(cost_dict['total'])

        for _, row in listing_metrics_config.iterrows():
            key = row['col']
            if row['db.type'] == 'Integer':
                if request.form[key] == '':
                    value = None
                else:
                    value = int(request.form[key])
            elif row['db.type'] == 'Boolean':
                value = key in request.form
            else:
                value = None
            setattr(listing, key, value)
        db.session.commit()
        return redirect(url_for('listings'))
    col_groups = listing_metrics_config['col_group'].drop_duplicates().values.tolist()
    cols = { row['col']:[ row['col_group'],row['db.type'], row['display_name']  ] for _, row in listing_metrics_config.iterrows() }
    return render_template('edit_listing.html', listing=listing, col_groups=col_groups, cols=cols)

@app.route('/listing/<int:listing_id>/delete', methods=['POST'])
def delete_listing(listing_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    listing = Listing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    return redirect(url_for('listings'))

@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != session['user_id']:
        return "Unauthorized", 403
    if request.method == 'POST':
        comment.content = request.form['content']
        db.session.commit()
        return redirect(url_for('listings'))
    return render_template('edit_comment.html', comment=comment)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != session['user_id']:
        return "Unauthorized", 403
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('listings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
