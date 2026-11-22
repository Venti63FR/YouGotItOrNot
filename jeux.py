from gagnant import *
from manche import *
from tableau import *
def jeux():
    nbjoueur=int(input("nombre de joueurs ?\n"))
    nbmanche=int(input("nombres de manches ?\n"))
    joueurs={}
    option={}
    for i in range(nbjoueur):
        print("nom joueur ",i," :")
        j=input("")
        joueurs[j]=0
        option[j]=[True,False,True,True,False]#[voler,tuvasskip,peuxfaireskip,bonus point,a eux 20 points]
    for i in range(nbmanche):
        manche(joueurs,nbmanche,i,option)
    tabscore(joueurs)
    gagnant(joueurs)

jeux()