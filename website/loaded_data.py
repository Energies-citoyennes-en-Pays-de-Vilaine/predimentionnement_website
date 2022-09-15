CA_REDON_POPULATION = 34_725
CA_REDON_RES_CONSUMPTION = 194_884 
CA_REDON_PRO_CONSUMPTION = 47_361  
CA_REDON_ENT_CONSUMPTION = 218_011 
CA_PONTCHATEAU_POPULATION = 16_226
CA_PONTCHATEAU_RES_CONSUMPTION = 98_603
CA_PONTCHATEAU_PRO_CONSUMPTION = 16_283
CA_PONTCHATEAU_ENT_CONSUMPTION = 50_986
NB_EOLIENNE = 19
PROD_PER_WINDTURBINE = 0.728 #average prod per wind turbine in MW
SOLAR_TOTAL_PROD = (0.728 * 365 * 24)
BIOENERGY_TOTAL_PROD = (0.69 * 365 * 24) 
PRODUCTION_SCALING_FACTOR = 1e6  / (365*24) / (CA_PONTCHATEAU_POPULATION + CA_REDON_POPULATION)

RES_TOTAL_CONSUMPTION = CA_REDON_RES_CONSUMPTION + CA_PONTCHATEAU_RES_CONSUMPTION
PRO_TOTAL_CONSUMPTION = CA_REDON_PRO_CONSUMPTION + CA_PONTCHATEAU_PRO_CONSUMPTION
ENT_TOTAL_CONSUMPTION = CA_REDON_ENT_CONSUMPTION + CA_PONTCHATEAU_ENT_CONSUMPTION

params = {
    "interactive" : 
    {
        "RES_TOTAL_CONSUMPTION" : RES_TOTAL_CONSUMPTION,
        "PRO_TOTAL_CONSUMPTION" : PRO_TOTAL_CONSUMPTION,
        "ENT_TOTAL_CONSUMPTION" : ENT_TOTAL_CONSUMPTION,
        "RES_CURVE_NAME"        : "courbe de consommation du panel résidentiel ENEDIS 2020 pour la région bretagne",
        "PRO_CURVE_NAME"        : "courbe de consommation du panel professionnel ENEDIS 2020 pour la région bretagne",
        "ENT_CURVE_NAME"        : "courbe de consommation du panel entreprise ENEDIS 2020 pour la région bretagne",
        "EOL_CURVE_NAME"        : "courbe de production éolienne du parc de Béganne 2021 corrigé pour correspondre a une production long terme",
        "SUN_CURVE_NAME"        : "courbe de production solaire ENEDIS 2020 pour la région bretagne",
        "BIO_CURVE_NAME"        : "courbe de production bioénergie ENEDIS 2020 pour la région bretagne"
    },
    "static": 
    {
        "RES_TOTAL_CONSUMPTION" : RES_TOTAL_CONSUMPTION,
        "PRO_TOTAL_CONSUMPTION" : PRO_TOTAL_CONSUMPTION,
        "ENT_TOTAL_CONSUMPTION" : ENT_TOTAL_CONSUMPTION,
        "RES_CURVE_NAME"        : "courbe de consommation du panel résidentiel ENEDIS 2020 pour la région bretagne",
        "PRO_CURVE_NAME"        : "courbe de consommation du panel professionnel ENEDIS 2020 pour la région bretagne",
        "ENT_CURVE_NAME"        : "courbe de consommation du panel entreprise ENEDIS 2020 pour la région bretagne",
        "EOL_CURVE_NAME"        : "courbe de production éolienne du parc de Béganne 2021 corrigé pour correspondre a une production long terme",
        "SUN_CURVE_NAME"        : "courbe de production solaire ENEDIS 2020 pour la région bretagne",
        "BIO_CURVE_NAME"        : "courbe de production bioénergie ENEDIS 2020 pour la région bretagne"
    }

}