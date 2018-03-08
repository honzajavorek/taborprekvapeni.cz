# taborprekvapeni.cz

Zdrojový kód webu letního dětského tábora s názvem _Tábor plný překvapení_.

## Instalace

1. Je potřeba Python 3. Přesná verze Pythonu je v souboru [runtime.txt](runtime.txt).
2. Je dobré si [vytvořit virtualenv](http://naucse.python.cz/course/pyladies/beginners/install/).
3. Do virtualenvu si nainstalujeme závislosti: `pip install -r requirements.txt`

## Vývoj

1. Spustíme `python runserver.py`
2. V prohlížeči jdeme na http://0.0.0.0:5000/

Můžeme dělat změny a pomocí [gitu](http://naucse.python.cz/course/pyladies/sessions/git/) je posílat na GitHub. Pokud si s gitem nechceme hrát v příkazové řádce, můžeme změny provedené na našem lokálním počítači posílat i pomocí klikacího programu [GitHub Desktop](https://desktop.github.com/).

## Jak se orientovat v kódu

Aplikace je napsaná ve frameworku [Flask](http://flask.pocoo.org/). Dělá spoustu zbytečností, protože dřív stahovala automaticky informace z tabory.cz. Toto se dnes již neděje, ale kód, který se o tuto automatiku staral, zde zůstal s námi. Asi by se dal web klidně předělat čistě na statické stránky. Nebo by se data mohla číst alespoň z [YAML](http://yaml.org/) souborů, a ne složitě parsovat nějaké vlastní výmysly v [Markdownu](https://guides.github.com/features/mastering-markdown/). No, to už je výzva pro další generace...

- `models` - Dynamicky získávaná data ze souborů nebo (původně) z internetu (tabory.cz).
- `models/photos.py` - Věc, která umí za běhu upravovat a zmenšovat obrázky. V šablonách se používá jako "image proxy".
- `static` - Obrázky, CSS, atd.
- `templates` - HTML prošpikované vkládanými daty, tzv. šablony. Jazyk šablon je [Jinja2](http://jinja.pocoo.org/).
- `cache.py` - Kešování obrázků a dat. Jednou se načtou a web si je chvíli pamatuje, než je načítá znova. Paměť má v adresáři `tmp`, který si podle potřeby vytváří.
- `templating.py` - Nástroje pro šablony.
- `views.py` - Samotné jednotlivé stránky (_controller_).

## Nasazení

- Každý _push_ do _master_ větve na GitHubu spustí automatický _build_ na [Heroku](http://heroku.com/).
- Heroku se podívá, jakou verzi Pythonu má použít. To zjistí ze souboru [runtime.txt](runtime.txt).
- Pak začne instalovat závislosti. Ty zjistí z [requirements.txt](requirements.txt)
- Když to má hotové, podívá se do [Procfile](Procfile), kde zjistí, že má spustit nějaký `gunicorn taborprekvapeni:app bla bla bla`. Ten spustí/restartuje.
- Tím jsou změny nasazeny na http://taborprekvapeni.cz

Gunicorn je server, který spustí Python aplikaci a vystaví ji ven. Je to totéž, co ten `python runserver.py`, akorát že ten je jen na odzkoušení a ladění. Gunicorn je rychlejší a neprůstřelnější, takže se hodí ve chvíli, kdy chceme web opravdu vystavit do světa.

## Další věci

- Přístup na GitHub má @honzajavorek a @brnkamatej
- Přístup na Heroku má @honzajavorek a @brnkamatej
- Přístup na Google Analytics má @honzajavorek
- Přístup na taborprekvapeni.cz doménu má @honzajavorek
