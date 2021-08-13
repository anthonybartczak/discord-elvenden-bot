ADV_TABLE = '''```
╔═════════════╦═══════════════════════════╗
║             ║ Koszt w PD za Rozwinięcie ║
║ Rozwinięcia ╠══════════╦════════════════╣
║             ║   Cechy  ║  Umiejętności  ║
╠═════════════╬══════════╬════════════════╣
║    0 do 5   ║    25    ║       10       ║
╠═════════════╬══════════╬════════════════╣
║   6 do 10   ║    30    ║       15       ║
╠═════════════╬══════════╬════════════════╣
║   11 do 15  ║    40    ║       20       ║
╠═════════════╬══════════╬════════════════╣
║   16 do 20  ║    50    ║       30       ║
╠═════════════╬══════════╬════════════════╣
║   21 do 25  ║    70    ║       40       ║
╠═════════════╬══════════╬════════════════╣
║   26 do 30  ║    90    ║       60       ║
╠═════════════╬══════════╬════════════════╣
║   31 do 35  ║    120   ║       80       ║
╠═════════════╬══════════╬════════════════╣
║   36 do 40  ║    150   ║       110      ║
╠═════════════╬══════════╬════════════════╣
║   41 do 45  ║    190   ║       140      ║
╠═════════════╬══════════╬════════════════╣
║   46 do 50  ║    230   ║       180      ║
╠═════════════╬══════════╬════════════════╣
║   51 do 55  ║    280   ║       220      ║
╠═════════════╬══════════╬════════════════╣
║   56 do 60  ║    330   ║       270      ║
╠═════════════╬══════════╬════════════════╣
║   61 do 65  ║    390   ║       320      ║
╠═════════════╬══════════╬════════════════╣
║   66 do 70  ║    450   ║       380      ║
╠═════════════╬══════════╬════════════════╣
║   ponad 70  ║    520   ║       440      ║
╚═════════════╩══════════╩════════════════╝```'''

MISCAST_MINOR = [
    '**Wiedźmi znak**\nPierwsza istota, która urodzi się w promieniu dwóch kilometrów, będzie zmutowana.',
    '**Skwaśniałe mleko**\nWszelkie mleko w promieniu 1k100 metrów natychmiast kwaśnieje.',
    '**Nieurodzaj**\nLiczbę pól uprawnych równą Bonusowi z Siły Woli w promieniu Bonus z Siły Woli kilometrów dotyka klęska żywiołowa i w ciągu jednej nocy wszystkie plony gniją',
    '**Woskowina**\nUszy czarodzieja natychmiast zatykają się przez nadmiar gęstej woskowiny. Postać otrzymuje 1 poziom Ogłuszenia, który nie może zostać usunięty, dopóki ktoś nie wyczyści uszu postaci (udany Test Leczenia).',
    '**Wiedźmi blask**\nNa 1k10 Rund postać żarzy się dziwnym blaskiem, który emituje tyle światła, co ognisko. Kolor zależny jest od Tradycji zaklęcia.',
    '**Straszliwe szepty**\nWykonaj Przeciętny (+20) Test Siły Woli. Jeśli się on nie powiedzie, postać otrzymuje 1 Punkt Zepsucia.',
    '**Krwotok**\nNos, oczy i uszy zaczynają obficie krwawić. Postać otrzymuje 1k10 poziomów Krwawienia.',
    '**Trzęsienie duszy**\nPostać zostaje Powalona.',
    '**Otwarcie**\nWszystkie klamry i troki przy ciele rzucającego rozpinają się i rozwiązują, co powoduje, że spadają pasy, otwierają się sakwy i torby, odpadają kawałki pancerza itd.',
    '**Krnąbrne odzienie**\nUbrania postaci zaczynają się skręcać, jakby nagle otrzymały wolną wolę. Postać otrzymuje 1 poziom Pochwycenia, którego Siła równa jest 1k10x5.',
    '**Klątwa abstynencji**\nWszelki alkohol w promieniu 1k100 metrów psuje się, staje się gorzki i paskudny w smaku.',
    '**Wyssanie duszy**\nPostać otrzymuje 1 poziom Zmęczenia, który utrzymuje się przez 1k10 godzin.',
    '**Rozproszenie uwagi**\nJeśli postać zaangażowana jest w walkę, staje się Zaskoczona. Jeśli nie jest to scena walki, postać ogarnia strach, serce wali jej jak młotem, nie jest w stanie skupić się na niczym przez kilka chwil.',
    '**Bezbożne wizje**\nPrzez krótką chwilę postać nawiedzają bluźniercze i bezbożne wizje. Postać otrzymuje 1 poziom Oślepienia i musi zdać Wymagający (+0) Test Opanowania albo otrzymuje kolejny poziom Oślepienia.',
    '**Język w supeł**\nWszystkie Testy językowe (w tym Testy Rzucenia Zaklęć) otrzymują karę -10 na 1k10 Rund.',
    '**Zgroza!**\nPostać musi zdać Trudny (-20) Test Opanowania albo otrzymuje 1 poziom Paniki.',
    '**Klątwa zepsucia**\nPostać otrzymuje 1 Punkt Zepsucia.',
    '**Przesunięcie**\nEfekt rzuconego zaklęcia pojawia się 2k10 kilometrów od rzucającego. W zależności od MG, jeśli to możliwe, taka sytuacja powinna mieć odpowiednie konsekwencje.',
    '**Wielopech**\nWykonaj dwa rzuty i zastosuj odpowiednie efekty obydwu. Przerzuć, jeśli kolejny wynik będzie się mieścił w przedziale 91-100.',
    '**Fala Chaosu**\nRzuć ponownie, ale tym razem porównaj efekt z Tabelą Większych Manifestacji.'
]

MISCAST_MAJOR = [
    '**Upiorne głosy**\nKażdy w promieniu tylu metrów, ile wynosi Siła Woli postaci, słyszy mroczne, nęcące szepty, które są emanacją Dziedziny Chaosu. Wszystkie myślące stworzenia muszą zdać Przeciętny (+20) Test Opanowania albo otrzymują 1 Punkt Zepsucia.',
    '**Przeklęty wzrok**\nOczy postaci nabierają nienaturalnego koloru, odpowiedniego dla Tradycji zaklęcia, na 1k10 godzin. W tym czasie postać cierpi z powodu 1 poziomu Oślepienia, co nie może zostać wyleczone ani rozproszone żadnym sposobem.',
    '**Wstrząs Eteru**\nPostać otrzymuje 1k10 Obrażeń, które ignorują Bonus z Wytrzymałości oraz Punkty Pancerza. Musi także zdać Przeciętny (+20) Test Odporności, w przeciwnym wypadku otrzyma również 1 poziom Oszołomienia.',
    '**Spacer śmierci**\nWszędzie, gdzie stąpa postać, pojawia się śmierć. Przez najbliższe 1k10 godzin wszelkie rośliny obok postaci usychają i giną.',
    '**Żołądkowa rewolucja**\nWnętrzności zaczynają poruszać się w niekontrolowany sposób, a postać wypróżnia się wbrew swojej woli. Otrzymuje 1 poziom Zmęczenia, którego nie da się usunąć inaczej niż kąpielą i zmianą ubrania.',
    '**Ogień duszy**\nPostać otrzymuje 1 poziom Podpalenia, trawiona przez potworne płomienie w kolorze Tradycji zaklęcia.',
    '**Dar języków**\nPostać przez 1k10 Rund trajkocze niezrozumiale. Podczas trwania tego efektu nie może porozumiewać się werbalnie ani podejmować Testów Rzucania Zaklęć, choć oprócz tego zachowuje się zupełnie normalnie.',
    '**Rój**\nPostać zostaje zaatakowana przez chmarę eterycznych szczurów, gigantycznych pająków, węży lub innych podobnych stworzeń (decyduje MG). Użyj standardowych charakterystyk, odpowiednich dla danego gatunku stworzenia, dodając Cechę Stworzenia Rój. Po 1k10 Rundach, jeśli nie zostały zniszczone wcześniej, stwory znikają.',
    '**Szmaciana lalka**\nPostać zostaje wyrzucona w powietrze i leci 1k10 metrów w losowym kierunku. Otrzymuje 1k10 Obrażeń ignorujących Punkty Pancerza, zostaje również Powalona.',
    '**Zmrożone kończyny**\nJedna kończyna (losowa) zostaje zamrożona na 1k10 godzin. Przez ten czas jest zupełnie bezużyteczna, jakby została Amputowana (patrz strona 180).',
    '**Mroczna ślepota**\nNa 1k10 godzin postać traci swój Talent Percepcja Magiczna. Wszelkie Testy Splatania Magii otrzymują karę -20.',
    '**Chaotyczna dalekowzroczność**\nOtrzymujesz premiową pulę 1k10 Punktów Szczęścia (które mogą przekroczyć normalny limit). Za każdym razem, gdy postać korzysta z tych punktów, otrzymuje 1 Punkt Zepsucia. Wszelkie pozostałe Punkty Szczęścia zdobyte w ten sposób przepadają po zakończeniu sesji gry.',
    '**Lewitacja**\nWiatry Magii porywają postać w powietrze. Na 1k10 minut unosi się 1k10 metrów nad ziemią. Inne postaci mogą ją przemieszczać siłą. Ponadto postać może poruszać się sama dzięki zaklęciom, skrzydłom i innym zabiegom, ale jeśli zostanie pozostawiona sama sobie, uniesie się z powrotem jak balonik. Lewitacja kończy się upadkiem (patrz strona 166).',
    '**Wymioty**\nPostać wymiotuje, wyrzucając z siebie o wiele więcej odrażająco śmierdzących wymiocin, niż mogłoby pomieścić ciało. Postać otrzymuje 1 poziom Oszołomienia, który utrzymuje się przez 1k10 Rund.',
    '**Trzęsienie Chaosu**\nWszystkie stworzenia w promieniu 1k100 metrów muszą zdać Przeciętny (+20) Test Atletyki albo zostaną Powalone.',
    '**Zdrada w sercu**\nMroczni Bogowie nakłaniają postać do wybitnie perfidnego czynu. Jeśli postać zaatakuje lub w inny sposób zdradzi sojusznika (z całą mocą i bez ograniczeń), odzyskuje wszystkie Punkty Szczęścia. Jeśli zmusi inną postać do wydania Punktu Przeznaczenia, sama otrzymuje 1 Punkt Przeznaczenia.',
    '**Plugawa niemoc**\nPostać otrzymuje 1 Punkt Zepsucia, 1 poziom Zmęczenia i zostaje Powalona.',
    '**Odór z piekła rodem**\nTo jest dopiero smród! Postać otrzymuje Cechę Stworzenia Dekoncentrujący (patrz strona 338), a najpewniej też wrogość czegokolwiek, co ma zmysł powonienia. Efekt utrzymuje się przez 1k10 godzin.',
    '**Wyssanie moc**\nPrzez 1k10 minut postać nie jest w stanie używać Talentów związanych z rzucaniem czarów (zazwyczaj Magii Tajemnej, choć może to być również Magia Chaosu lub podobny Talent).',
    '**Reakcja Eteru**\nKażdy – wróg czy przyjaciel – w promieniu tylu metrów, ile wynosi Bonus z Siły Woli postaci, otrzymuje 1k10 Obrażeń, które ignorują Bonus z Wytrzymałości i Punkty Pancerza. Wszyscy w tym promieniu zostają też Powaleni. Jeśli na tym obszarze nie ma żadnych celów, magia nie ma się gdzie ulotnić, więc wzbiera wewnątrz czaszki, rozsadzając ją od środka. Postać ginie natychmiast.'
]