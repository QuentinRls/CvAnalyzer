@echo off
echo 🏗️  Construction du frontend...
cd frontend
call npm run build
cd ..

echo 🚀 Démarrage de l'application complète...
python main.py

pause
