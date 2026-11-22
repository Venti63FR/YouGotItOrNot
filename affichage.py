def affiFilm( nbmanche , mancheencours , joueur ,score, replique,  nomfilmcacher="" , indice=False,):
    print("score : ",score,"nom du joueur : ",joueur,"\n")
    print("manche ",mancheencours,"/",nbmanche-1,"\n") 
    print("entre 0 pour voler des points a quelqu'un")
    print("entre 1 pour faire passer le tour a quelqu'un choisie  aleatoirement")
    print("entre 2 pour avoir des points bonus")
    print("la replique de film: \n",replique,"\n")
    if indice ==True:
        print("Votre indice est : ",nomfilmcacher,"\n")

    print("Quel est le nom du film ?\n")

def affiReal( nbmanche , mancheencours , joueur ,score, replique, nomdufilm):
    print("score : ",score,"nom du joueur : ",joueur,"\n")
    print("manche ",mancheencours,"/",nbmanche-1,"\n") 
    print("entre 0 pour voler des points a quelqu'un")
    print("entre 1 pour faire passer le tour a quelqu'un choisie aleatoirement")
    print("entre 2 pour avoir des points bonus")
    print("Le film est : ",nomdufilm,"\n")
    print("Quel est le nom et prenom  du realisateur ? \n")



