def gagnant(joueurs):
    joueurmax= None
    scoremax=0
    for joueur,score in joueurs.items():
        if score>=scoremax:
            scoremax=score
            joueurmax=joueur
    print("le gagnant est",joueurmax,"avec",scoremax,"points")
    return joueurmax