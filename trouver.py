    
def trouver(res,dicofilm,mode):
    if (mode == "f" and  res.upper()==dicofilm["film"].upper()) or  (mode == "r" and res.upper()==dicofilm["realisateur"].upper()) :
        print("Bonne reponse !!!")
        return True
    else:
        print("Mauvaise reponse")
        return False
