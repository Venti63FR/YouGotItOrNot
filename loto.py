import random
from score import * 
def luck(joueuractu, dicojoueur,option):
    if option[joueuractu][3]:
        option[joueuractu][3]=False
        tirage =random.randint(0,1000000)
        intervale=0
        if  tirage <= 950000:
            tirage = random.randint(0,4)
            intervale=tirage
        elif 950000<tirage<=990000 :
            tirage =random.randint(0,5)
            intervale=tirage+4
        elif 990000<tirage<=999999:
            tirage = random.randint(0,5)
            intervale=tirage + 9
        else : 
            tirage = random.randint(0,6)
            intervale =tirage + 14
        if intervale != 20:
            print("Bravo tu as gagné ",intervale," points !!!\n")
            score(dicojoueur, joueuractu , intervale)
        else :
            print(" bravo tu as gagné 20 points !!!! tu as une chance sur 6 000 000 de tomber la dessus , pour feter ca on met ton score a 1 points , quelle aubaine .\n")
            score(dicojoueur, joueuractu , 1-dicojoueur[joueuractu])
            option[joueuractu][4]=True
    else:
        print("tu as deja utilisé ce bonus , dommage ... \n")
    input("appuie sur entre pour continuer\n")

     