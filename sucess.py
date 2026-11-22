def suces(dicojoueur,option):
    print(" voici le path of pain :")
    for j in dicojoueur :
        if option[j][4] :
            print(j," a debloqué le suces Ange dechu: obtenir le bonus de 20 point, puis retomber a 1 points\n tu aurais pu tomber bien plus bas \n")
        if dicojoueur[j] >=250 :
            print(j," a debloqué le suces Le Connaiseur :obtenir 20 points en une partie \n T'as pas autre chose a faire de ton temps ?\n")
        if dicojoueur[j] >= 500 :
            print(j," a debloqué le suces The Wather : obtenir 500 points en une partie \n Tu es un vrai cinephile toi !!!\n")
        if dicojoueur[j] >=1000 :
            print(j," a debloqué le suces LA Reference :obtenir 1000 points en une partie \n Les jeunes toujours sur leurs ecrans !!!\n")
        if dicojoueur[j]==66 :
            print(j," a debloqué le suces Le site : avoir 66 points \n Executer l'ordre 60 sith\n")
        if dicojoueur[j]==666:
            print(j," a debloqué le suces Diabolique :obtenir 666 points \n Sa t'en bouche un coin\n")        
