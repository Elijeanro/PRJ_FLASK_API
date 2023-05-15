from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "articledb.sqlite")
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Les Classes de la base de données -------------------------------------------------------------
class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=True)

    def __init__(self, *args, **kwargs):
        super(Categorie, self).__init__(*args, **kwargs)
    

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    prix = db.Column(db.Float, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'),
        nullable=False)
    
    
    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
    

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    client = db.Column(db.String(80), nullable=False)
    articles = db.relationship('Article', secondary='article_commande',
        backref=db.backref('commandes', lazy='dynamic'))
    
    
    def __init__(self, *args, **kwargs):
        super(Commande, self).__init__(*args, **kwargs)
    

class ArticleCommande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'),
        nullable=False)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'),
        nullable=False)
    
    
    def __init__(self, *args, **kwargs):
        super(ArticleCommande, self).__init__(*args, **kwargs)
    

# Les schémas ------------------------------------------------------------------------------------------------
class CategorieSchema(ma.Schema):
    class Meta:
        fields = ("id", "nom", "description")


categorie_schema = CategorieSchema()
categories_schema = CategorieSchema(many=True)

class ArticleSchema(ma.Schema):
    class Meta:
        fields = ("id", "nom", "description","prix","quantite","categorie_id")


article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)

class CommandeSchema(ma.Schema):
    class Meta:
        fields = ("id", "date", "client","articles")


commande_schema = CommandeSchema()
commandes_schema = CommandeSchema(many=True)

class ArticleCommandeSchema(ma.Schema):
    class Meta:
        fields = ("id", "nom", "description")


articleCommande_schema = ArticleCommandeSchema()
articleCommandes_schema = ArticleCommandeSchema(many=True)

# Création de la base de données ----------------------------------------------------------------------

with app.app_context():
    db.create_all()
    print('Base de données créée !')

# Création des différentes routes ----------------------------------------------------------------------
#--------------------------Articles---------------------------------------------------------------------

@app.route("/article", methods=["POST"])
def add_article():
    nom = request.args.get["nom"]
    description = request.args.get["description"]
    prix = request.args.get["prix"]
    quantite = request.args.get["quantite"]
    categorie_id = request.args.get["categorie_id"]
    
    new_article = Article(nom, description, prix, quantite, categorie_id)

    db.session.add(new_article)
    db.session.commit()

    return article_schema.jsonify(new_article)


@app.route("/article", methods=["GET"])
def get_articles():
    all_articles = Article.query.all()
    result = articles_schema.dump(all_articles)
    return jsonify(result)


@app.route("/article/<id>", methods=["GET"])
def get_article(id):
    article = Article.query.get(id)
    return article_schema.jsonify(article)


@app.route("/article/<id>", methods=["PUT"])
def update_article(id):
    article = Article.query.get(id)
    if article is None:
        return jsonify({"message": "L'article n'a pas été trouvé."}), 404
    
    nom = request.args.get("nom")
    description = request.args.get("description")
    prix = request.args.get("prix")
    quantite = request.args.get("quantite")
    categorie_id = request.args.get("categorie_id")

    article.nom = nom
    article.description = description
    article.prix = prix
    article.quantite = quantite
    article.categorie_id = categorie_id

    db.session.commit()

    return article_schema.jsonify(article)


@app.route("/article/<id>", methods=["DELETE"])
def delete_article(id):
    article = Article.query.get(id)
    db.session.delete(article)
    db.session.commit()
    return article_schema.jsonify(article)

@app.route("/article/recherche", methods=["GET"])
def search_article():
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({"message": "Veuillez fournir un mot-clé pour effectuer la recherche."}), 400
    articles = Article.query.filter(Article.nom.ilike(f"%{keyword}%")).all()
    if not articles:
        return jsonify({"message": "Aucun article n'a été trouvé pour ce mot-clé."}), 404
    return articles_schema.jsonify(articles)

#-----------------------------------categorie-------------------------------------------------

@app.route("/categorie", methods=["POST"])
def add_categorie():
    nom = request.args.get("nom")
    description = request.args.get("description")

    new_categorie = Categorie(nom=nom, description=description)

    db.session.add(new_categorie)
    db.session.commit()

    return categorie_schema.jsonify(new_categorie)


@app.route("/categorie", methods=["GET"])
def get_categories():
    all_categories = Categorie.query.all()
    result = categories_schema.dump(all_categories)
    return jsonify(result)


@app.route("/categorie/<id>", methods=["GET"])
def get_categorie(id):
    categorie = Categorie.query.get(id)
    return categorie_schema.jsonify(categorie)


@app.route("/categorie/<id>", methods=["PUT"])
def update_categorie(id):
    categorie = Categorie.query.get(id)
    if categorie is None:
        return jsonify({"message": "La catégorie n'a pas été trouvée."}), 404
    nom = request.args.get("nom")
    description = request.args.get("description")
    
    categorie.nom = nom
    categorie.description = description
    
    db.session.commit()

    return categorie_schema.jsonify(categorie)


@app.route("/categorie/<id>", methods=["DELETE"])
def delete_categorie(id):
    categorie = Categorie.query.get(id)
    db.session.delete(categorie)
    db.session.commit()
    return categorie_schema.jsonify(categorie)

#---------------------------------Commande------------------------------------------------------

@app.route("/commande", methods=["POST"])
def add_commande():
    date = request.args.get["date"]
    client = request.args.get["client"]
    article = request.args.get["article"]
    
    new_commande = Commande(date, client, article)

    db.session.add(new_commande)
    db.session.commit()

    return commande_schema.jsonify(new_commande)


@app.route("/commande", methods=["GET"])
def get_commandes():
    all_commandes = Commande.query.all()
    result = commandes_schema.dump(all_commandes)
    return jsonify(result)


@app.route("/commande/<id>", methods=["GET"])
def get_commande(id):
    commande = Commande.query.get(id)
    return commande_schema.jsonify(commande)


@app.route("/commande/<id>", methods=["PUT"])
def update_commande(id):
    commande = Commande.query.get(id)
    if commande is None:
        return jsonify({"message": "La commande n'a pas été trouvée."}), 404
    
    date = request.args.get("date")
    client = request.args.get("client")
    article = request.args.get("article")
    
    commande.date = date
    commande.client = client
    commande.article = article
    

    db.session.commit()

    return commande_schema.jsonify(commande)


@app.route("/commande/<id>", methods=["DELETE"])
def delete_commande(id):
    commande = Commande.query.get(id)
    db.session.delete(commande)
    db.session.commit()
    return commande_schema.jsonify(commande)

#------------------------ArticleCommande---------------------------------------------
@app.route("/articleCommande", methods=["POST"])
def add_articleCommande():
    article_id = request.args.get["article_id"]
    commande_id = request.args.get["commande_id"]
    
    new_articleCommande = ArticleCommande(article_id, commande_id)

    db.session.add(new_articleCommande)
    db.session.commit()

    return articleCommande_schema.jsonify(new_articleCommande)


@app.route("/articleCommande", methods=["GET"])
def get_articleCommandes():
    all_articleCommandes = ArticleCommande.query.all()
    result = articleCommandes_schema.dump(all_articleCommandes)
    return jsonify(result)


@app.route("/articleCommande/<id>", methods=["GET"])
def get_articleCommande(id):
    articleCommande = ArticleCommande.query.get(id)
    return articleCommande_schema.jsonify(articleCommande)


@app.route("/articleCommande/<id>", methods=["PUT"])
def update_articleCommande(id):
    articleCommande = ArticleCommande.query.get(id)
    if articleCommande is None:
        return jsonify({"message": "La ligne de Commande n'a pas été trouvée."}), 404
    
    article_id = request.args.get("article_id")
    commande_id = request.args.get("commande_id")
    
    articleCommande.article_id = article_id
    articleCommande.commande_id = commande_id
    
    db.session.commit()

    return articleCommande_schema.jsonify(articleCommande)


@app.route("/articleCommande/<id>", methods=["DELETE"])
def delete_articleCommande(id):
    articleCommande = ArticleCommande.query.get(id)
    db.session.delete(articleCommande)
    db.session.commit()
    return articleCommande_schema.jsonify(articleCommande)


if __name__ == "__main__":
    app.run(debug=True)