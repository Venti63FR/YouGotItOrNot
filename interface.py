"""
DONT PANIC !!! You have the ref ?  -  interface pygame

Pensée pour un seul écran partagé :
  - PC : à afficher / projeter dans une salle (grosse typo, F11 = plein écran)
  - Téléphone : on se passe l'appareil de joueur en joueur (clavier tactile intégré)

Lancer :  python interface.py
          python interface.py --portrait   (force le format téléphone vertical)
          python interface.py --paysage    (force le format écran de PC)
"""
import math
import random
import re
import sys
import threading
import unicodedata

import pygame

from replique import renvoieDeDonnee
from cacherlettre import masq
from trouver import trouver
from score import score

# --------------------------------------------------------------------------- #
#  Réglages
# --------------------------------------------------------------------------- #
POINTS = [100, 80, 50, 25]      # points selon l'essai (film)
POINTS_REAL = 20                # points pour le réalisateur
MAX_JOUEURS = 8
MAX_MANCHES = 20
TITRE = "DONT PANIC !!! You have the ref ?"

C = {
    "bg_top": (26, 28, 64),
    "bg_bot": (9, 10, 26),
    "panel": (36, 40, 82),
    "panel2": (56, 62, 116),
    "text": (240, 242, 255),
    "muted": (150, 158, 204),
    "gold": (255, 196, 61),
    "green": (72, 200, 120),
    "red": (240, 84, 96),
    "pink": (236, 72, 153),
    "blue": (90, 150, 255),
    "off": (46, 48, 72),
    "dark": (18, 19, 40),
}

pygame.init()
_info = pygame.display.Info()
if "--portrait" in sys.argv:
    _size = (405, 720)                                 # simule un téléphone sur PC
elif "--paysage" in sys.argv:
    _size = (1280, 720)
elif _info.current_h > _info.current_w:                # téléphone en vertical : plein écran
    _size = (_info.current_w, _info.current_h)
else:
    _size = (1280, 720)
window = pygame.display.set_mode(_size, pygame.RESIZABLE)
pygame.display.set_caption(TITRE)
clock = pygame.time.Clock()

# On dessine sur une surface "logique" dont le format suit celui de la fenêtre
# (téléphone très allongé, PC 16:9, rotation de l'écran...), puis on la met à l'échelle.
W, H, M, PORTRAIT = 1280, 720, 32, False
PAD_TOP = PAD_BOT = 16                                 # marges de sécurité (encoche, barre de gestes)
SCALE, OFFSET = 1.0, (0, 0)
screen = pygame.Surface((W, H))


def update_layout():
    """Recalcule la taille logique si la fenêtre change. Renvoie True si elle a changé."""
    global window, screen, W, H, M, PORTRAIT, PAD_TOP, PAD_BOT, SCALE, OFFSET
    window = pygame.display.get_surface()
    ww, wh = window.get_size()
    portrait = wh > ww
    if portrait:
        nw, nh = 720, max(1000, min(1700, round(720 * wh / ww)))
    else:
        nw, nh = max(1000, min(1800, round(720 * ww / wh))), 720
    SCALE = min(ww / nw, wh / nh)
    OFFSET = ((ww - nw * SCALE) / 2, (wh - nh * SCALE) / 2)
    if (nw, nh) == (W, H) and portrait == PORTRAIT:
        return False
    W, H, PORTRAIT = nw, nh, portrait
    screen = pygame.Surface((W, H))
    M = 24 if portrait else 32
    PAD_TOP, PAD_BOT = (30, 22) if portrait else (16, 16)
    return True


def to_logical(pos):
    return ((pos[0] - OFFSET[0]) / SCALE, (pos[1] - OFFSET[1]) / SCALE)


def present():
    """Affiche la surface logique dans la fenêtre (mise à l'échelle + bandes noires si besoin)."""
    window.fill((0, 0, 0))
    size = (round(W * SCALE), round(H * SCALE))
    if size == (W, H):
        window.blit(screen, (round(OFFSET[0]), round(OFFSET[1])))
    else:
        zoom = pygame.transform.smoothscale if size[0] * size[1] < 2500000 else pygame.transform.scale
        window.blit(zoom(screen, size), (round(OFFSET[0]), round(OFFSET[1])))
    pygame.display.flip()


update_layout()

# --------------------------------------------------------------------------- #
#  Petits outils
# --------------------------------------------------------------------------- #
_fonts = {}


def font(size, bold=False):
    key = (int(size), bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("segoeui,helvetica,arial,dejavusans", int(size), bold=bold)
    return _fonts[key]


def wrap(text, f, max_w):
    lignes = []
    for para in text.split("\n"):
        cur = ""
        for mot in para.split(" "):
            test = (cur + " " + mot).strip()
            if f.size(test)[0] <= max_w or not cur:
                cur = test
            else:
                lignes.append(cur)
                cur = mot
        lignes.append(cur)
    return lignes


def make_background():
    surf = pygame.Surface((W, H))
    for y in range(H):
        t = y / H
        col = tuple(int(C["bg_top"][i] * (1 - t) + C["bg_bot"][i] * t) for i in range(3))
        pygame.draw.line(surf, col, (0, y), (W, y))
    return surf


def norm(s):
    """Minuscules, sans accents ni ponctuation : 'Amélie' == 'amelie'."""
    s = s.lower().replace("œ", "oe").replace("æ", "ae")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def tirage_bonus():
    """Même loterie que loto.py : renvoie un nombre de points entre 0 et 20."""
    t = random.randint(0, 1000000)
    if t <= 950000:
        return random.randint(0, 4)
    if t <= 990000:
        return random.randint(0, 5) + 4
    if t <= 999999:
        return random.randint(0, 5) + 9
    return random.randint(0, 6) + 14


ROWS = [
    [(c, 1) for c in "1234567890"],
    [(c, 1) for c in "AZERTYUIOP"],
    [(c, 1) for c in "QSDFGHJKLM"],
    [(c, 1) for c in "WXCVBN'-"] + [("Eff.", 2)],
    [("Espace", 7), ("OK", 3)],
]

# (titre, condition, petite phrase, test(score_final, options_du_joueur))
SUCCES = [
    ("Ange déchu", "Tirer le bonus de 20 points, puis retomber à 1 point",
     "Tu aurais pu tomber bien plus bas.", lambda s, o: o[4]),
    ("Le Connaisseur", "Atteindre 250 points en une partie",
     "T'as pas autre chose à faire de ton temps ?", lambda s, o: s >= 250),
    ("The Watcher", "Atteindre 500 points en une partie",
     "Tu es un vrai cinéphile, toi !", lambda s, o: s >= 500),
    ("LA Référence", "Atteindre 1000 points en une partie",
     "Les jeunes, toujours sur leurs écrans !", lambda s, o: s >= 1000),
    ("Le Sith", "Finir la partie avec exactement 66 points",
     "Exécutez l'ordre 66.", lambda s, o: s == 66),
    ("Diabolique", "Finir la partie avec exactement 666 points",
     "Ça t'en bouche un coin.", lambda s, o: s == 666),
]


# --------------------------------------------------------------------------- #
#  Application
# --------------------------------------------------------------------------- #
class App:
    def __init__(self):
        self.bg = make_background()
        self.state = "setup"
        self.click = None
        self.mouse = (0, 0)
        self.kb = False                 # clavier tactile affiché ?
        self.modal = None
        # réglages de partie
        self.nb_joueurs = 2
        self.nb_manches = 3
        self.names = [""] * MAX_JOUEURS
        self.active = 0
        # partie
        self.noms, self.joueurs, self.option = [], {}, {}
        self.manche = self.idx = 0
        self.token = 0
        self.film = self.err = None
        self.confetti = []
        self.notices = []
        self.phase, self.essai, self.gain = "film", 0, 0
        self.answer, self.hint, self.msg = "", "", ("", C["muted"])
        self.dir_ok = False
        self.succes, self.succes_page = [], 0

    # ----- événements ------------------------------------------------------ #
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.click = to_logical(e.pos)
            elif e.type == pygame.FINGERDOWN and not self.kb and self.state in ("setup", "question"):
                self.kb = True                       # premier toucher : on sort le clavier
            elif e.type == pygame.TEXTINPUT:
                self.type_text(e.text)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    self.backspace()
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.enter()
                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
        self.mouse = to_logical(pygame.mouse.get_pos())

    def buffer(self):
        if self.state == "setup":
            return self.names[self.active], 16
        if self.state == "question" and not self.modal:
            return self.answer, 60
        return None, 0

    def set_buffer(self, val):
        if self.state == "setup":
            self.names[self.active] = val
        else:
            self.answer = val

    def type_text(self, txt):
        buf, limite = self.buffer()
        if buf is not None and txt.isprintable() and len(buf) + len(txt) <= limite:
            self.set_buffer(buf + txt)

    def backspace(self):
        buf, _ = self.buffer()
        if buf:
            self.set_buffer(buf[:-1])

    def enter(self):
        if self.state == "setup":
            self.active = min(self.active + 1, self.nb_joueurs - 1)
        elif self.state == "question" and not self.modal:
            self.submit()

    # ----- widgets (mode immédiat : on dessine ET on teste le clic) -------- #
    def txt(self, text, size, color, pos, anchor="topleft", bold=False, max_w=None):
        f = font(size, bold)
        if max_w:
            while f.size(text)[0] > max_w and size > 12:
                size -= 2
                f = font(size, bold)
        img = f.render(text, True, color)
        r = img.get_rect(**{anchor: pos})
        screen.blit(img, r)
        return r

    def button(self, rect, label, color=None, enabled=True, size=28, primary=False):
        rect = pygame.Rect(rect)
        hover = enabled and rect.collidepoint(self.mouse)
        down = hover and pygame.mouse.get_pressed()[0]
        base = C["gold"] if primary else (color or C["panel2"])
        if not enabled:
            base = C["off"]
        col = tuple(max(0, v - 30) for v in base) if down else (
            tuple(min(255, v + 18) for v in base) if hover else base)
        pygame.draw.rect(screen, C["dark"], rect.move(0, 4), border_radius=14)
        pygame.draw.rect(screen, col, rect, border_radius=14)
        tc = C["dark"] if primary else (C["text"] if enabled else C["muted"])
        self.txt(label, size, tc, rect.center, "center", bold=True, max_w=rect.w - 16)
        if enabled and self.click is not None and rect.collidepoint(self.click):
            self.click = None                    # un clic = une seule action
            return True
        return False

    def panel(self, rect, color=None, border=None):
        pygame.draw.rect(screen, color or C["panel"], rect, border_radius=18)
        if border:
            pygame.draw.rect(screen, border, rect, 3, border_radius=18)

    def stepper(self, rect, label, value, lo, hi):
        rect = pygame.Rect(rect)
        self.panel(rect)
        self.txt(label, 26, C["muted"], (rect.x + 20, rect.centery), "midleft")
        bw = rect.h - 14
        minus = pygame.Rect(rect.right - 2 * bw - 100, rect.y + 7, bw, bw)
        plus = pygame.Rect(rect.right - bw - 7, rect.y + 7, bw, bw)
        self.txt(str(value), 36, C["gold"], ((minus.right + plus.x) // 2, rect.centery), "center", bold=True)
        if self.button(minus, "-", enabled=value > lo, size=34):
            value -= 1
        if self.button(plus, "+", enabled=value < hi, size=34):
            value += 1
        return value

    def kb_h(self):
        if not self.kb:
            return 0
        return min(470, int(H * 0.30)) if PORTRAIT else int(H * 0.38)

    def keyboard(self):
        kb_h = self.kb_h()
        area = pygame.Rect(0, H - kb_h, W, kb_h)
        pygame.draw.rect(screen, C["dark"], area)
        gap = 6
        key_h = (kb_h - PAD_BOT - 6 * gap) / 5
        for r, row in enumerate(ROWS):
            unit = (W - gap * (len(row) + 1)) / sum(w for _, w in row)
            x, y = gap, area.y + gap + r * (key_h + gap)
            for label, w in row:
                rect = pygame.Rect(round(x), round(y), round(unit * w), round(key_h))
                if self.button(rect, label, size=int(key_h * 0.5), primary=(label == "OK")):
                    if label == "Eff.":
                        self.backspace()
                    elif label == "Espace":
                        self.type_text(" ")
                    elif label == "OK":
                        self.enter()
                    else:
                        self.type_text(label)
                x += unit * w + gap

    def input_box(self, rect, text, placeholder):
        rect = pygame.Rect(rect)
        self.panel(rect, C["dark"], C["gold"])
        f = font(32)
        shown = text
        while f.size(shown)[0] > rect.w - 36 and shown:
            shown = shown[1:]
        if text:
            r = self.txt(shown, 32, C["text"], (rect.x + 18, rect.centery), "midleft")
            cx = r.right + 3
        else:
            self.txt(placeholder, 28, C["muted"], (rect.x + 18, rect.centery), "midleft")
            cx = rect.x + 18
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            pygame.draw.line(screen, C["gold"], (cx, rect.centery - 18), (cx, rect.centery + 18), 3)

    def scoreboard(self, rect, highlight=None):
        rect = pygame.Rect(rect)
        classement = sorted(self.noms, key=lambda n: -self.joueurs[n])
        cols = 2 if (len(classement) > 4 and not PORTRAIT) else 1
        rows = math.ceil(len(classement) / cols)
        rh = min(52, rect.h // max(rows, 1))
        cw = rect.w // cols
        for i, nom in enumerate(classement):
            col, row = divmod(i, rows)
            r = pygame.Rect(rect.x + col * cw + 4, rect.y + row * rh, cw - 8, rh - 6)
            self.panel(r, C["panel2"] if nom == highlight else C["panel"])
            self.txt(f"{i + 1}", 24, C["gold"], (r.x + 18, r.centery), "midleft", bold=True)
            self.txt(nom, 26, C["text"], (r.x + 58, r.centery), "midleft", bold=nom == highlight, max_w=r.w - 190)
            self.txt(f"{self.joueurs[nom]} pts", 26, C["gold"], (r.right - 18, r.centery), "midright", bold=True)

    def spinner(self, center, r=26):
        t = pygame.time.get_ticks() / 1000
        for i in range(10):
            a = i / 10 * 2 * math.pi
            k = (1 - ((t * 1.5 - i / 10) % 1)) ** 2
            col = tuple(int(C["bg_bot"][c] + (C["gold"][c] - C["bg_bot"][c]) * k) for c in range(3))
            pygame.draw.circle(screen, col, (center[0] + r * math.cos(a), center[1] + r * math.sin(a)), 5 + 3 * k)

    def fit(self, text, rect, color, max_size, min_size, bold=False):
        """Écrit le texte centré, avec la plus grande police qui tient dans rect."""
        for size in range(max_size, min_size - 1, -2):
            f = font(size, bold)
            lignes = wrap(text, f, rect.w)
            if len(lignes) * f.get_linesize() <= rect.h:
                break
        y = rect.y + (rect.h - len(lignes) * f.get_linesize()) // 2
        for l in lignes:
            img = f.render(l, True, color)
            screen.blit(img, img.get_rect(midtop=(rect.centerx, y)))
            y += f.get_linesize()

    # ----- logique de partie ------------------------------------------------ #
    def start_game(self):
        noms = []
        for i in range(self.nb_joueurs):
            nom = self.names[i].strip() or f"Joueur {i + 1}"
            while nom in noms:
                nom += "'"
            noms.append(nom)
        self.noms = noms
        self.joueurs = {n: 0 for n in noms}
        # [voler, tuvasskip, peuxfaireskip, bonus point, a eu 20 points]
        self.option = {n: [True, False, True, True, False] for n in noms}
        self.manche, self.idx = 0, -1
        self.modal = None
        self.next_player()

    def next_player(self):
        self.notices = []
        while True:
            self.idx += 1
            if self.idx >= len(self.noms):
                self.idx, self.manche = 0, self.manche + 1
            if self.manche >= self.nb_manches:
                self.state = "end"
                self.confetti = [[random.uniform(0, W), random.uniform(-H, 0), random.uniform(2, 5),
                                  random.choice([C["gold"], C["pink"], C["blue"], C["green"]]),
                                  random.randint(6, 12)] for _ in range(90)]
                self.succes, self.succes_page = self.calcul_succes(), 0
                return
            nom = self.noms[self.idx]
            if self.option[nom][1]:                  # ce joueur a été "skippé"
                self.option[nom][1] = False
                self.notices.append(f"{nom} passe son tour !")
                continue
            break
        self.phase, self.essai, self.gain = "film", 0, 0
        self.answer, self.hint, self.msg = "", "", ("", C["muted"])
        self.state = "pass"
        self.load_film()                             # chargé pendant l'écran "passe l'appareil"

    def load_film(self):
        self.token += 1
        t = self.token
        self.film, self.err = None, None

        def work():
            try:
                data = renvoieDeDonnee()
                if t == self.token:
                    self.film = data
            except Exception as ex:
                if t == self.token:
                    self.err = str(ex) or ex.__class__.__name__

        threading.Thread(target=work, daemon=True).start()

    def check(self, rep, mode):
        f = self.film
        ok = trouver(norm(rep), {"film": norm(f["film"]), "realisateur": norm(f["realisateur"])}, mode)
        if not ok and mode == "r":                   # "Nom Prénom" accepté aussi
            ok = sorted(norm(rep).split()) == sorted(norm(f["realisateur"]).split())
        return ok

    def submit(self):
        rep = self.answer.strip()
        if not rep or self.film is None:
            return
        joueur = self.noms[self.idx]
        self.answer = ""
        if self.phase == "film":
            if self.check(rep, "f"):
                pts = POINTS[self.essai]
                score(self.joueurs, joueur, pts)
                self.gain += pts
                self.msg = (f"Bonne réponse ! +{pts} points", C["green"])
                self.phase, self.hint = "real", ""
            else:
                self.essai += 1
                if self.essai == len(POINTS):
                    self.msg = ("Raté... le film est révélé", C["red"])
                    self.phase, self.hint = "real", ""
                else:
                    self.msg = ("Mauvaise réponse", C["red"])
                    if self.essai >= 2:
                        self.hint = masq(self.film["film"])
        else:
            self.dir_ok = self.check(rep, "r")
            if self.dir_ok:
                score(self.joueurs, joueur, POINTS_REAL)
                self.gain += POINTS_REAL
            self.state = "result"

    # ----- bonus ------------------------------------------------------------ #
    def do_voler(self, cible):
        j = self.noms[self.idx]
        self.option[j][0] = False
        pts = round(self.joueurs[cible] * 0.3)
        self.joueurs[j] += pts
        self.joueurs[cible] -= pts
        self.modal = ("info", f"Tu voles {pts} points à {cible} !")

    def do_skip(self):
        j = self.noms[self.idx]
        self.option[j][2] = False
        cible = random.choice(self.noms)
        self.option[cible][1] = True
        self.modal = ("info", f"{cible} passera son prochain tour !")

    def do_luck(self):
        j = self.noms[self.idx]
        self.option[j][3] = False
        pts = tirage_bonus()
        if pts != 20:
            score(self.joueurs, j, pts)
            self.modal = ("info", f"Bravo, tu as gagné {pts} points !")
        else:
            score(self.joueurs, j, 1 - self.joueurs[j])
            self.option[j][4] = True
            self.modal = ("info", "20 points !!! Une chance sur 6 000 000... "
                                  "pour fêter ça, ton score tombe à 1 point. Quelle aubaine.")

    def powerups(self, rect):
        o = self.option[self.noms[self.idx]]
        rect = pygame.Rect(rect)
        gap = 10
        w = (rect.w - 2 * gap) // 3
        defs = [("Voler", o[0] and len(self.noms) > 1, ("voler",)),
                ("Skip", o[2], ("skip",)),
                ("Bonus", o[3], None)]
        for i, (label, ok, modal) in enumerate(defs):
            r = pygame.Rect(rect.x + i * (w + gap), rect.y, w, rect.h)
            if self.button(r, label, color=C["pink"], enabled=ok, size=26):
                if modal:
                    self.modal = modal
                else:
                    self.do_luck()

    # ----- écrans ----------------------------------------------------------- #
    def screen_setup(self):
        avail = H - self.kb_h()
        compact = (not PORTRAIT) and self.kb
        y = PAD_TOP
        if compact:
            self.txt(TITRE, 34, C["gold"], (W // 2, y + 24), "center", bold=True, max_w=W - 2 * M - 300)
            y += 62
        else:
            self.txt("DONT PANIC !!!", 56 if PORTRAIT else 64, C["gold"], (W // 2, y + 66), "center", bold=True)
            self.txt("You have the ref ?", 30, C["muted"], (W // 2, y + 114), "center")
            y += 150
        cw = W - 2 * M
        if PORTRAIT:
            self.nb_joueurs = self.stepper((M, y, cw, 64), "Joueurs", self.nb_joueurs, 1, MAX_JOUEURS)
            self.nb_manches = self.stepper((M, y + 74, cw, 64), "Manches", self.nb_manches, 1, MAX_MANCHES)
            y += 156
            fields = pygame.Rect(M, y, cw, 0)
            cols, rh = 1, 58
            start = pygame.Rect(M, avail - 80 - PAD_BOT, cw, 76)
        else:
            lw = 440
            self.nb_joueurs = self.stepper((M, y, lw, 64), "Joueurs", self.nb_joueurs, 1, MAX_JOUEURS)
            self.nb_manches = self.stepper((M, y + 76, lw, 64), "Manches", self.nb_manches, 1, MAX_MANCHES)
            start = pygame.Rect(M, y + 160, lw, 84)
            fields = pygame.Rect(M + lw + 28, y, cw - lw - 28, 0)
            cols, rh = 2, 62
        for i in range(self.nb_joueurs):
            col, row = (i % cols, i // cols) if cols == 2 else (0, i)
            w = fields.w // cols
            r = pygame.Rect(fields.x + col * w, fields.y + row * rh, w - (10 if cols == 2 else 0), rh - 10)
            if self.click is not None and r.collidepoint(self.click):
                self.active = i
                self.click = None
            self.panel(r, C["dark"], C["gold"] if i == self.active else C["panel2"])
            nom = self.names[i]
            if nom:
                t = self.txt(nom, 28, C["text"], (r.x + 16, r.centery), "midleft", max_w=r.w - 40)
                cx = t.right + 3
            else:
                self.txt(f"Joueur {i + 1}", 26, C["muted"], (r.x + 16, r.centery), "midleft")
                cx = r.x + 16
            if i == self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(screen, C["gold"], (cx, r.centery - 15), (cx, r.centery + 15), 3)
        if self.button(start, "Lancer la partie", primary=True, size=34):
            self.start_game()
        if self.button((W - M - 130, PAD_TOP - 6, 130, 38), "Clavier", color=C["blue"] if self.kb else C["panel2"], size=22):
            self.kb = not self.kb
        if self.kb:
            self.keyboard()

    def screen_pass(self):
        nom = self.noms[self.idx]
        y = H * 0.07
        for n in self.notices:
            self.txt(n, 28, C["pink"], (W // 2, y), "center", bold=True)
            y += 38
        y = max(y, H * 0.10)
        self.txt("Passe l'appareil à", 34, C["muted"], (W // 2, y + 20), "center")
        self.txt(nom, 80 if PORTRAIT else 96, C["gold"], (W // 2, y + 105), "center", bold=True, max_w=W - 2 * M)
        self.txt(f"Manche {self.manche + 1}/{self.nb_manches}", 28, C["muted"], (W // 2, y + 180), "center")
        bw = min(520, W - 2 * M)
        by = y + 220
        if self.button((W // 2 - bw // 2, by, bw, 90), "Je suis prêt !", primary=True, size=40):
            self.state = "question"
        self.scoreboard(pygame.Rect(M, by + 120, W - 2 * M, H - by - 120 - M), nom)

    def screen_question(self):
        j = self.noms[self.idx]
        kb_h = self.kb_h()
        avail = H - kb_h
        x0, cw = M, W - 2 * M
        y = PAD_TOP
        self.txt(j, 34, C["text"], (x0, y), bold=True, max_w=(cw if PORTRAIT else cw - 520))
        self.txt(f"Manche {self.manche + 1}/{self.nb_manches}   ·   {self.joueurs[j]} pts", 22, C["muted"], (x0, y + 40))
        if PORTRAIT:
            y += 70
            self.powerups((x0, y, cw, 54))
            y += 54 + 12
        else:
            self.powerups((W - M - 500, y, 500, 54))
            y += 70

        if self.film is None:                        # chargement / erreur
            card = pygame.Rect(x0, y, cw, avail - y - M)
            self.panel(card)
            if self.err:
                self.txt("Impossible de récupérer un film", 34, C["red"], (card.centerx, card.centery - 50), "center", bold=True)
                self.txt("Vérifie la connexion internet", 24, C["muted"], (card.centerx, card.centery - 10), "center")
                if self.button((card.centerx - 130, card.centery + 30, 260, 64), "Réessayer", primary=True):
                    self.load_film()
            else:
                self.txt("Chargement du film...", 32, C["text"], (card.centerx, card.centery + 50), "center")
                self.spinner((card.centerx, card.centery - 20))
            if kb_h:
                self.keyboard()
            return

        film_phase = self.phase == "film"
        self.txt("Quel est le nom du film ?" if film_phase else "Qui est le réalisateur ? (prénom et nom)",
                 30, C["gold"], (x0, y), bold=True, max_w=cw)
        y += 40

        # zones du bas, calculées depuis le bas : la carte prend tout le reste
        input_h, msg_h, pips_h, hint_h = 60, 36, 38, 34
        bottom = avail - PAD_BOT
        in_rect = pygame.Rect(x0, bottom - input_h, cw - 230, input_h)
        bottom -= input_h + 8
        msg_rect = pygame.Rect(x0, bottom - msg_h, cw, msg_h)
        bottom -= msg_h + 6
        pips_rect = pygame.Rect(x0, bottom - pips_h, cw, pips_h)
        bottom -= pips_h + 6
        hint_rect = None
        if self.hint and film_phase:
            hint_rect = pygame.Rect(x0, bottom - hint_h, cw, hint_h)
            bottom -= hint_h + 6

        # carte avec la réplique (bords façon pellicule)
        card = pygame.Rect(x0, y, cw, max(80, bottom - y))
        if PORTRAIT and card.h > 640:                # évite une carte géante en vertical
            card.y += (card.h - 640) // 2
            card.h = 640
        self.panel(card)
        for x in range(card.x + 20, card.right - 20, 28):
            pygame.draw.rect(screen, C["bg_bot"], (x, card.y + 7, 14, 8), border_radius=3)
            pygame.draw.rect(screen, C["bg_bot"], (x, card.bottom - 15, 14, 8), border_radius=3)
        zone = card.inflate(-70, -50)
        if film_phase:
            self.txt("«", 90, C["panel2"], (card.x + 18, card.y + 10), bold=True)
            self.fit(self.film["replique"], zone, C["text"], 44, 18)
        else:
            self.txt("Le film est :", 26, C["muted"], (card.centerx, card.y + 40), "center")
            self.fit(self.film["film"], pygame.Rect(zone.x, zone.y + 20, zone.w, zone.h - 20), C["gold"], 64, 24, True)

        if hint_rect:
            lettres = " ".join("_" if c in "* " else c for c in self.hint)
            self.txt("Indice :", 24, C["muted"], (hint_rect.x, hint_rect.centery), "midleft")
            self.txt(lettres, 30, C["gold"], (hint_rect.x + 110, hint_rect.centery), "midleft", bold=True,
                     max_w=hint_rect.w - 120)

        # pastilles de points
        labels = [str(p) for p in POINTS] if film_phase else [f"Réalisateur +{POINTS_REAL}"]
        pw = 110 if film_phase else 260
        for i, lab in enumerate(labels):
            r = pygame.Rect(pips_rect.x + i * (pw + 10), pips_rect.y, pw, pips_rect.h)
            actif = (not film_phase) or i == self.essai
            pygame.draw.rect(screen, C["gold"] if actif else C["panel"], r, border_radius=19)
            self.txt(lab, 24, C["dark"] if actif else C["muted"], r.center, "center", bold=True)
            if film_phase and i < self.essai:
                pygame.draw.line(screen, C["red"], (r.x + 14, r.centery), (r.right - 14, r.centery), 3)

        # message + bouton clavier
        self.txt(self.msg[0], 26, self.msg[1], (msg_rect.x, msg_rect.centery), "midleft", bold=True, max_w=cw - 190)
        if self.button((msg_rect.right - 150, msg_rect.y, 150, msg_rect.h), "Clavier",
                       color=C["blue"] if self.kb else C["panel2"], size=20):
            self.kb = not self.kb

        # saisie
        self.input_box(in_rect, self.answer, "Nom du film" if film_phase else "Prénom Nom")
        if self.button((in_rect.right + 10, in_rect.y, 220, input_h), "Valider", primary=True, size=30):
            self.submit()
        if kb_h:
            self.keyboard()

    def screen_result(self):
        j = self.noms[self.idx]
        f = self.film
        y = H * 0.07
        self.txt("Le film était", 28, C["muted"], (W // 2, y), "center")
        self.fit(f["film"], pygame.Rect(M, y + 20, W - 2 * M, 90), C["gold"], 56, 24, True)
        y += 140
        self.txt("Réalisateur : " + f["realisateur"], 32, C["green"] if self.dir_ok else C["red"],
                 (W // 2, y), "center", bold=True, max_w=W - 2 * M)
        y += 48
        self.txt(f"{j} gagne {self.gain} points ce tour" if self.gain else f"{j} ne marque pas ce tour",
                 30, C["text"], (W // 2, y), "center")
        y += 40
        bw = min(520, W - 2 * M)
        by = H - M - 90
        self.scoreboard(pygame.Rect(M, y + 10, W - 2 * M, by - y - 30), j)
        if self.button((W // 2 - bw // 2, by, bw, 84), "Continuer", primary=True, size=38):
            self.next_player()

    def screen_end(self):
        for c in self.confetti:
            c[1] += c[2]
            if c[1] > H:
                c[0], c[1] = random.uniform(0, W), -10
            pygame.draw.rect(screen, c[3], (c[0], c[1], c[4], c[4] * 0.6))
        best = max(self.joueurs.values())
        gagnants = [n for n in self.noms if self.joueurs[n] == best]
        y = H * 0.08
        self.txt("Fin de la partie !", 40, C["muted"], (W // 2, y), "center")
        titre = gagnants[0] if len(gagnants) == 1 else "Égalité : " + " & ".join(gagnants)
        self.txt(titre, 80 if len(gagnants) == 1 else 50, C["gold"], (W // 2, y + 80), "center", bold=True, max_w=W - 2 * M)
        self.txt(f"{best} points", 34, C["text"], (W // 2, y + 150), "center")
        by = H - M - 84
        self.scoreboard(pygame.Rect(M, y + 190, W - 2 * M, by - y - 210))
        bw = (W - 2 * M - 28) // 3
        if self.button((M, by, bw, 84), "Rejouer", primary=True, size=32):
            self.state = "setup"
        if self.button((M + bw + 14, by, bw, 84), f"Succès ({len(self.succes)})", color=C["pink"],
                       enabled=bool(self.succes), size=30):
            self.state = "succes"
        if self.button((M + 2 * (bw + 14), by, bw, 84), "Quitter", size=32):
            pygame.quit()
            sys.exit()

    def calcul_succes(self):
        res = []
        for nom in self.noms:
            for titre, desc, quip, test in SUCCES:
                if test(self.joueurs[nom], self.option[nom]):
                    res.append({"nom": nom, "titre": titre, "desc": desc, "quip": quip})
        return res

    def screen_succes(self):
        self.txt("Succès débloqués", 44, C["gold"], (W // 2, PAD_TOP + 40), "center", bold=True)
        cols = 1 if PORTRAIT else 2
        gap, ch = 12, 140
        top = PAD_TOP + 90
        by = H - M - 76
        rows = max(1, (by - 16 - top) // (ch + gap))
        per = rows * cols
        pages = max(1, math.ceil(len(self.succes) / per))
        self.succes_page = min(self.succes_page, pages - 1)
        cw = (W - 2 * M - (cols - 1) * gap) // cols
        debut = self.succes_page * per
        for k, sc in enumerate(self.succes[debut:debut + per]):
            r = pygame.Rect(M + (k % cols) * (cw + gap), top + (k // cols) * (ch + gap), cw, ch)
            self.panel(r, C["panel"], C["gold"])
            self.txt(sc["titre"], 30, C["gold"], (r.x + 18, r.y + 12), bold=True, max_w=r.w - 36)
            self.txt(sc["nom"], 24, C["pink"], (r.x + 18, r.y + 50), bold=True, max_w=r.w - 36)
            self.txt(sc["desc"], 21, C["muted"], (r.x + 18, r.y + 82), max_w=r.w - 36)
            self.txt(sc["quip"], 21, C["text"], (r.x + 18, r.y + 108), max_w=r.w - 36)
        if pages > 1:
            bw = (W - 2 * M - 14) // 2
            if self.button((M, by, bw, 76), "Retour", size=30):
                self.state = "end"
            if self.button((M + bw + 14, by, bw, 76), f"Page {self.succes_page + 1}/{pages}", primary=True, size=28):
                self.succes_page = (self.succes_page + 1) % pages
        elif self.button((W // 2 - 160, by, 320, 76), "Retour", primary=True, size=30):
            self.state = "end"

    # ----- fenêtres modales ------------------------------------------------- #
    def draw_modal(self):
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 175))
        screen.blit(veil, (0, 0))
        kind = self.modal[0]
        pw = min(W - 2 * M, 760)
        if kind == "voler":
            cibles = [n for n in self.noms if n != self.noms[self.idx]]
            cols = 2 if len(cibles) > 4 else 1
            rows = math.ceil(len(cibles) / cols)
            box = pygame.Rect(0, 0, pw, 150 + rows * 66 + 80)
            box.center = (W // 2, H // 2)
            self.panel(box, C["panel"], C["pink"])
            self.txt("Voler 30 % des points de...", 34, C["text"], (box.centerx, box.y + 50), "center",
                     bold=True, max_w=pw - 40)
            bw = (pw - 40 - (cols - 1) * 10) // cols
            for i, n in enumerate(cibles):
                col, row = divmod(i, rows)
                r = pygame.Rect(box.x + 20 + col * (bw + 10), box.y + 100 + row * 66, bw, 56)
                if self.button(r, f"{n}  ({self.joueurs[n]})", size=26):
                    self.do_voler(n)
            if self.button((box.centerx - 120, box.bottom - 76, 240, 56), "Annuler", size=26):
                self.modal = None
        elif kind == "skip":
            box = pygame.Rect(0, 0, pw, 330)
            box.center = (W // 2, H // 2)
            self.panel(box, C["panel"], C["pink"])
            self.txt("Skip", 40, C["text"], (box.centerx, box.y + 50), "center", bold=True)
            for k, l in enumerate(wrap("Un joueur tiré au hasard (peut-être toi !) passera son prochain tour.",
                                       font(28), pw - 60)):
                self.txt(l, 28, C["muted"], (box.centerx, box.y + 110 + k * 36), "center")
            bw = (pw - 60) // 2
            if self.button((box.x + 20, box.bottom - 90, bw, 64), "Lancer le tirage", primary=True, size=26):
                self.do_skip()
            if self.button((box.x + 40 + bw, box.bottom - 90, bw, 64), "Annuler", size=26):
                self.modal = None
        else:  # info
            lignes = wrap(self.modal[1], font(32, True), pw - 60)
            box = pygame.Rect(0, 0, pw, 130 + len(lignes) * 42 + 90)
            box.center = (W // 2, H // 2)
            self.panel(box, C["panel"], C["gold"])
            for k, l in enumerate(lignes):
                self.txt(l, 32, C["text"], (box.centerx, box.y + 70 + k * 42), "center", bold=True)
            if self.button((box.centerx - 110, box.bottom - 80, 220, 60), "OK", primary=True, size=30):
                self.modal = None

    # ----- boucle principale ------------------------------------------------ #
    def run(self):
        while True:
            if update_layout():
                self.bg = make_background()
            self.events()
            screen.blit(self.bg, (0, 0))
            click = self.click
            if self.modal:
                self.click = None                    # rien ne réagit sous la fenêtre modale
            getattr(self, "screen_" + self.state)()
            if self.modal:
                self.click = click
                self.draw_modal()
            self.click = None
            present()
            clock.tick(60)


if __name__ == "__main__":
    App().run()
