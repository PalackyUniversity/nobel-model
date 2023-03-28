# Covid model

## Data
- https://www.czso.cz/documents/142154812/176236044/sldb2021_pv_vek_pohlavi.xlsx
- https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-demografie.csv
- https://www.czso.cz/documents/10180/179851740/demomigr_2005_2021_komplet.zip/
- https://www.czso.cz/documents/10180/179851750/demomigr_2022_predbezna_2022t51.zip/

## Modelované dle reality

- Struktura společnosti ze Sčítání lidu 2021
- Vakcinace z oficiálních dat z ÚZISU
- Počty úmrtí od ČSÚ
- Přecházení mezi jednotlivými věkovými skupinami v čase + rození lidí

## Parametr P
- pokud **P = 0** - vakcinace probíhá nezávisle na tom, zda daný člověk vypadá na umření
- pokud **P > 0** - člověk na umření (parametr TIMEDELTA) je z pravděpodobností P nevakcinován

## Parametr TIMEDELTA
- Definuje člověka na umření -- pokud je vakcinace určena blíže než TIMEDELTA týdnů od data úmrtí, je aplikován krok výše (Parametr P)

## Ukázkový výstup 

### Účinnost vakcín pro kategorii 80-129

#### P = 0, TIMEDELTA = 2 týdny

![efficacy P=0 TIMEDELTA=2](result/efficacy/age=80-129__TIMEDELTA_WEEKS=2__P=0.png)

#### P = 0.5, TIMEDELTA = 2 týdny

![efficacy P=0.5 TIMEDELTA=2](result/efficacy/age=80-129__TIMEDELTA_WEEKS=2__P=0.5.png)

#### P = 0.5, TIMEDELTA = 4 týdny

![efficacy P=0.5 TIMEDELTA=4](result/efficacy/age=80-129__TIMEDELTA_WEEKS=4__P=0.5.png)

#### P = 0.1, TIMEDELTA = 52 týdnů (~ 1 rok)

![efficacy P=0.1 TIMEDELTA=52](result/efficacy/age=80-129__TIMEDELTA_WEEKS=52__P=0.1.png)

### Sanity checks

![vaccination](result/vaccination.png)

![population](result/alive_derivative/age=80-129__TIMEDELTA_WEEKS=52__P=0.1.png)

