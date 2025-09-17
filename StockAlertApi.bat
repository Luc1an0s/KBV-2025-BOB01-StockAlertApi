@echo off
REM Ativa o ambiente virtual
call "C:\Users\Lucius\Documents\GitHub\KBV-PROJETOS\KBV-2025-BOB01 (StockAlertApi)\env-kbv\Scripts\activate.bat"

REM Roda o script Python
python "C:\Users\Lucius\Documents\GitHub\KBV-PROJETOS\KBV-2025-BOB01 (StockAlertApi)\StockAlertApi2.0.py"

REM Desativa o ambiente virtual (opcional)
deactivate