import random 
def masq(nomdufilm):
    nblettre= len(nomdufilm)
    nblettredonnee=round((30*nblettre)/100)
    numlettredonne=[]
    i=0
    while i < nblettredonnee:
        nbrand=random.randint(0,nblettre-1)
        if nbrand not in numlettredonne:
            numlettredonne.append(nbrand)
            i+=1
    motcacher="*" * nblettre
    motcacher=list(motcacher)
    for i in numlettredonne:
        motcacher[i]=nomdufilm[i]
    motcacher="".join(motcacher)
    return motcacher


