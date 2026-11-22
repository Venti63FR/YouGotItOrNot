import random
def saut(joueuractu,dicojoueur, option) :
    flag=True 
    if option[joueuractu][2]:
        option[joueuractu][2]=False 
        while flag :
            choix =input("tu vas faire passer le tour de quelqu'un choisie aleatoirement ,entre -1 si tu changes d'avis, entrée sinon ?" )       
            if choix =='-1' :
                input("appuie entrer pour sortir \n")
                flag=False
                option[joueuractu][2]=True
            else :
                cible = random.choice(list(dicojoueur.keys()))
                option[cible][1]=True
                flag=False
    else :
        print("tu as deja utilisé ce bonus!!!\n")