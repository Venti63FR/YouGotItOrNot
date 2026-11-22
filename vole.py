def voler (joueuractu, dicojoueur, option):
    flag=True 
    if option[joueuractu][0]:
        option[joueuractu][0]=False 
        while flag :
            cible = input("tu veux voler 30% des points a quel joueur(entre -1 si tu changes d'avis) ?" )
            if cible in dicojoueur:
                dicojoueur[joueuractu]+=round(dicojoueur[cible]*0.3)
                dicojoueur[cible]-=round(dicojoueur[cible]*0.3)
                print("nouveau compte de point : \n",joueuractu," : ",dicojoueur[joueuractu]," points\n",cible," : ",dicojoueur[cible]," points\n")
                flag=False
            elif cible =='-1' :
                input("appuie entrer pour sortir \n")
                flag=False
                option[joueuractu][0]=True
            else :
                print("le joueur n'existe pas , reessaie !!!\n")
    else :
        print("tu as deja utilisé ce bonus!!!\n")