import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pygame
import time


def image_load(name, transparency=True):
  image = pygame.image.load(name).convert()

  if transparency:
    image.set_colorkey(image.get_at((0, 0)))

  return image


def kolor(liczba):
    if liczba > 1:
        liczba = 1

    if liczba < 0.1:
        czerwony = 0
    if liczba < 0.45:
        czerwony = (566 + 2/3)*liczba
    elif liczba < 0.8:
        czerwony = 255
    else:
        czerwony = 1275*(1 - liczba)

    zielony = max(0, -2081.632653061*(liczba - 0.1)*(liczba - 0.8))

    if liczba < 0.1:
        niebieski = 100 + 1550*liczba
    elif liczba < 0.45:
        niebieski = 255
    elif liczba < 0.6:
        niebieski = 1020 - 1700*liczba
    else:
        niebieski = 0

    return (czerwony, zielony, niebieski)


def waga(wsp1, wsp2):
    return np.cos(np.pi*wsp2/180) - np.cos(np.pi*wsp1/180)


def do(start_date=1880):
    daty = []
    temperatury = []

    historyczne = []
    f = open('file.txt', 'r')
    for i, linijka in enumerate(f):
        if i >= 90*139:
            historyczne.append(eval(linijka))

    ds = nc.Dataset('dane.nc')
    tempanomaly = ds['tempanomaly']

    A = 16.4746543779
    C = -0.33352301803

    dol = 6.284166529774666
    maxi = 12.422499761
    stala = 1.0078

    dodatkowy_rozmiar, poprawka = 2, 4

    pygame.init()
    myfont = pygame.font.SysFont(None, 50)
    myfont2 = pygame.font.SysFont(None, 25)
    myfont3 = pygame.font.SysFont(None, 35)

    screen = pygame.display.set_mode((900, 90*(5 + dodatkowy_rozmiar) - (5 + dodatkowy_rozmiar)*2*poprawka + 97))
    image = pygame.image.load('MAPA.tif')

    wag = []

    i = (start_date - 1880)*12
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if i < 1680:
            data = int(1880 + (i + 1)/12) - 1
            rok = myfont.render('Rok:{}'.format(data), 1, (0, 0, 0))

            if not i%12:
                wartosci = np.zeros((90, 180))
                suma, wagi = 0, 0

            for j in range(90):
                wartosci[j] += np.array(tempanomaly[i, j, 0:180])

                for k in np.array(tempanomaly[i, j, 0:180]):
                    if k < 2500:
                        wzor = abs(abs(2*j - 90) - 90)
                        w = waga(wzor + 2, wzor)

                        if len(wag) < 90:
                            wag.append(w)

                        suma += k*w
                        wagi += w

            if i%12 == 11:
                liczba = suma/wagi
                daty.append(data)
                temperatury.append(liczba + 14)

                temp = myfont.render('Temp.:{}'.format(round(14 + liczba, 3)), 1, (0, 0, 0))
                if liczba < 0:
                    zm_temp = myfont3.render(str(round(liczba, 3)), 1, (0, 255, 0))
                else:
                    zm_temp = myfont3.render('+' + str(round(liczba, 3)), 1, (0, 255, 0))

                wartosci = list(wartosci/12)
                for j in range(poprawka, 90-poprawka):
                    for k in range(180):

                            iteracje = 0
                            while wartosci[j][k] > 2500:
                                wartosci[j][k] -= 2730.583251953
                                iteracje += 1

                            if iteracje < 12:
                                pygame.draw.rect(screen, kolor((wartosci[j][k] + dol)/(maxi + 1.476)), (k*5, (89 - poprawka - j)*(5 + dodatkowy_rozmiar), 5, (5 + dodatkowy_rozmiar)))
                            else:
                                pygame.draw.rect(screen, (128, 128, 128), (k*5, (89 - poprawka - j)*(5 + dodatkowy_rozmiar), 5, (5 + dodatkowy_rozmiar)))

                screen.blit(image, (0, 0))
                pygame.draw.rect(screen, (0, 128, 0), (0, 574, 900, 97))
                screen.blit(rok, (5, 584))
                screen.blit(temp, (5, 634))

                probka = (maxi + 1.476)/649
                aktualnie = -6
                mozna_rysowac = True
                for j in range(650):
                    color = j/649

                    pygame.draw.rect(screen, kolor(color), (220 + j, 579, 1, 25))
                    if j*probka - dol > aktualnie:
                        pygame.draw.rect(screen, (0, 0, 0), (220 + j, 579, 1, 40))
                        screen.blit(myfont2.render(str(aktualnie), 1, (0, 0, 0)), (215 + j, 619))
                        aktualnie += 1

                    if mozna_rysowac and j*probka - dol > liczba:
                        pygame.draw.rect(screen, (0, 255, 0), (219 + j, 579, 3, 40))
                        screen.blit(zm_temp, (180 + j, 640))
                        mozna_rysowac = False

        else:
            if i == 1680:
                plt.plot(daty, temperatury, 'k-o')
                plt.title('Średnia temperatura Ziemi z okresu {}-2019'.format(start_date))
                plt.ylabel('Temperatura')
                plt.xlabel('Rok')
                plt.grid()
                plt.show()

            data += 1
            B = A - liczba - 14
            rok = myfont.render('Rok:{}'.format(data), 1, (0, 0, 0))

            W = np.zeros((90, 180))
            suma, wagi = 0, 0

            for j in range(90):
                for k in range(180):
                    W[j][k] = wartosci[j][k] + (B - B*np.e**(C*(i - 1679)))*historyczne[j]*stala

                    iteracje = 0
                    while W[j][k] > 2500:
                        W[j][k] -= 2730.583251953
                        iteracje += 1

                    wzor = abs(abs(2*j - 90) - 90)
                    w = waga(wzor + 2, wzor)
                    suma += W[j][k]*w
                    wagi += w

                    if iteracje < 12 and j not in [0, 1, 2, 3, 86, 87, 88, 89]:
                        pygame.draw.rect(screen, kolor((W[j][k] + dol)/(maxi + B)), (k*5, (89 - poprawka - j)*(5 + dodatkowy_rozmiar), 5, (5 + dodatkowy_rozmiar)))
                    else:
                        pygame.draw.rect(screen, (128, 128, 128), (k*5, (89 - poprawka - j)*(5 + dodatkowy_rozmiar), 5, (5 + dodatkowy_rozmiar)))

            liczba2 = suma/wagi

            temp = myfont.render('Temp.:{}'.format(round(14 + liczba2, 3)), 1, (0, 0, 0))
            if liczba2 < 0:
                zm_temp = myfont3.render(round(liczba2, 3), 1, (0, 255, 0))
            else:
                zm_temp = myfont3.render('+' + str(round(liczba2, 3)), 1, (0, 255, 0))

                screen.blit(image, (0, 0))
                pygame.draw.rect(screen, (0, 128, 0), (0, 574, 900, 97))
                screen.blit(rok, (5, 584))
            screen.blit(temp, (5, 634))

            probka = (maxi + 1.476)/649
            aktualnie = -6
            mozna_rysowac = True
            for j in range(650):
                color = j/649

                pygame.draw.rect(screen, kolor(color), (220 + j, 579, 1, 25))
                if j*probka - dol > aktualnie:
                    pygame.draw.rect(screen, (0, 0, 0), (220 + j, 579, 1, 40))
                    screen.blit(myfont2.render(str(aktualnie), 1, (0, 0, 0)), (215 + j, 619))
                    aktualnie += 1

                if mozna_rysowac and j*probka - dol > liczba2:
                    pygame.draw.rect(screen, (0, 255, 0), (219 + j, 579, 3, 40))
                    screen.blit(zm_temp, (180 + j, 640))
                    mozna_rysowac = False

            time.sleep(1)

        pygame.display.flip()
        i += 1


if __name__ == '__main__':
    do(2015)
