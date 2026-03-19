-- Mockowanie globalnego obiektu gry
g_currentMission = {
    getMoney = function(self) return 125000 end,
    controlledVehicle = {
        getLastSpeed = function(self) return 42.5 end
    }
}

-- Symulacja API modów
function addModEventListener(listener)
    print("[MOCK] Zarejestrowano listener. Symulacja update()...")
    -- Wywołanie update() symulujące 30 sekund gry
    listener:update(30000)
end

-- Twoje pliki moda
require("scripts.LiveDashboard")