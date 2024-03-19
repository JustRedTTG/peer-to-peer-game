function()
    fill_screen(LOADING_SCREEN_BG)
    if not PRE_REGISTERED_ALL_MODS then
        for mod in get_all_mods() do
            load_mod(mod)
        end
        PRE_REGISTERED_ALL_MODS = true
    end
end