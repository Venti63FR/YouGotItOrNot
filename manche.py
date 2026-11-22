from affichage import *
from cacherlettre import *
from replique import *
from score import *
from trouver import *
from net import *
from vole import *
from skip import *
from loto import *
def manche(dicojoueur,nbmanche, nummanche , option ):
    for j in dicojoueur:
        if option[j][1]:
            option[j][1]=False
            continue
        dicofilm=renvoieDeDonnee()
        clear()
        affiFilm(nbmanche,nummanche,j,dicojoueur[j],dicofilm["replique"])
        rep=input("")
        if rep == '0':
            voler(j,dicojoueur,option)
        elif rep == '1':
            saut(j,dicojoueur,option)
        elif rep == '2':
            luck(j,dicojoueur, option)
        elif  trouver(rep,dicofilm,'f'):
            score(dicojoueur, j,100)
        else:
            clear()
            affiFilm(nbmanche,nummanche,j,dicojoueur[j],dicofilm["replique"])
            rep=input("")
            if rep == '0':
                voler(j,dicojoueur,option)
            elif rep == '1':
                saut(j,dicojoueur,option)
            elif rep == '2':
                luck(j,dicojoueur, option)
            elif  trouver(rep,dicofilm,'f'):
                score(dicojoueur, j,80)

            else :
                    clear()
                    affiFilm(nbmanche,nummanche,j,dicojoueur[j],dicofilm["replique"], masq(dicofilm["film"]),True)
                    rep=input("")
                    if rep == '0':
                        voler(j,dicojoueur,option)
                    elif rep == '1':
                            saut(j,dicojoueur,option)
                    elif rep == '2':
                        luck(j,dicojoueur, option)
                    elif trouver(rep,dicofilm,'f'):
                        score(dicojoueur, j,50)

                    else:
                            clear()
                            affiFilm(nbmanche,nummanche,j,dicojoueur[j],dicofilm["replique"], masq(dicofilm["film"]),True)
                            rep=input("")
                            if rep == '0':
                                voler(j,dicojoueur,option)
                            elif rep == '1':
                                saut(j,dicojoueur,option)
                            elif rep == '2':
                                luck(j,dicojoueur, option)

                            elif  trouver(rep,dicofilm,'f'):
                                score(dicojoueur, j,25)
        clear()
        affiReal(nbmanche,nummanche,j,dicojoueur[j],dicofilm["realisateur"],dicofilm["film"])
        rep=input("")
        if rep == '0':
            voler(j,dicojoueur,option)
        elif rep == '1':
                saut(j,dicojoueur,option)
        elif rep == '2':
            luck(j,dicojoueur, option)
        elif  trouver(rep,dicofilm,'f'):
            score(dicojoueur, j,20)

        


        