var districtStyle = {
    fillColor: "transparent",
    color: "white",
    weight: 2.25,
    dashArray: '3',
    opacity: 1,
    fillOpacity: 0.8
};



function farmerStyle(feature) {
    return {
    color: "white",
    dashArray: '3',
    fillColor: farmerColors[tables[feature.properties.baunit_type]],
    weight: 0.75,
    opacity: 1,
    fillOpacity: 0.8
    }
};

//bu_type_land_dehkan_auction

// bu_type_agricultural_enterprises - Korxonalarning qishloq xo‘jaligi yerlari

//bu_type_land_private --Yakka tartibda bog‘dorchilik, sabzavotchilik, issiqxona va chorvachilikni yurituvchi fuqarolarning yerlari

//bu_type_land_reserve Zaxiradagi qishloq xo‘jaligiga mo‘ljallangan yer uchastkasi

const tables = {
    "bu_type_land_ancillary": '1',
    "bu_type_land_highways": '2',
    "bu_type_land_dehkan": '3',
    "bu_type_bad_land": '4',
    "bu_type_land_r_and_d": '5',
    "bu_type_land_farm": '6',
    "bu_type_land_pasture": '7',
    "bu_type_land_private": '8',
    "bu_type_land_dehkan_auction": '9',
    "bu_type_land_farm_auction": '10',
    "bu_type_land_reserve": '11',
    "bu_type_agricultural_enterprises": '12',
    "bu_type_land_forest": '13',
    "bu_type_land_household": '14',
};

const farmerColors = [ "#248DCE", "#2A99E2", "#2D63E2", "#10A3C4", "#137DC4", "#5AB2C6", "#16BDE2", "#469DB0", "#196096", "#2FA19D", "#3DD5CD", "#425CA4", "#54B0E1", "#4884DF" ];