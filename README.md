# Fotowoltaika (Sofar Local)

Własna integracja Home Assistant do odczytu falownika SOFAR (testowana na
4.4KTLX-G3) bezpośrednio z loggera Wi-Fi po TCP (port 8899, protokół Solarman V5),
bez chmury.

- Domena: `sofar_local`
- Odczyt: 4 bloki rejestrów Modbus co kilka sekund
- Encje: moc, energia (dziś / razem), napięcia i prądy faz AC, stringi DC,
  temperatury, czasy pracy, status `Online`
- Gdy falownik nocą się wyłącza, integracja przechodzi w tryb offline
  (odpytywanie co 60 s, moc i prądy = 0) i wraca sama po wschodzie słońca.
- Po restarcie HA czujniki pokazują ostatnią znaną wartość, zanim falownik odpowie.

## Instalacja (HACS)

1. HACS → Integracje → menu ⋮ → Własne repozytoria.
2. Adres: `https://github.com/VoyteckPL/ha-sofar-local`, kategoria: Integration.
3. Pobierz, zrestartuj HA, dodaj integrację w Ustawienia → Urządzenia i usługi
   i podaj adres IP loggera, port (domyślnie 8899) oraz numer seryjny loggera.

Adres IP i numer seryjny są przechowywane tylko w konfiguracji Twojego HA,
nie w tym repozytorium.
