--
-- PostgreSQL database dump
--

\restrict p8DfzQyD8DE2tHzyFUc4EDjap4JaD6GjUElTzeLheqwoYa7zwhtf6Yxqc7B6dns

-- Dumped from database version 18.1 (Ubuntu 18.1-1.pgdg24.04+2)
-- Dumped by pg_dump version 18.1 (Ubuntu 18.1-1.pgdg24.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: modelo_wefe; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA modelo_wefe;


ALTER SCHEMA modelo_wefe OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: validacion_historica_mexico; Type: TABLE; Schema: modelo_wefe; Owner: postgres
--

CREATE TABLE modelo_wefe.validacion_historica_mexico (
    anio integer NOT NULL,
    poblacion_real bigint NOT NULL,
    pib_real numeric(20,2) NOT NULL,
    prod_granos_real numeric(18,2),
    prod_hortalizas_real numeric(18,2),
    prod_frutas_real numeric(18,2),
    prod_carne_real numeric(18,2),
    prod_lacteos_real numeric(18,2),
    oferta_agua_total numeric(18,2),
    demanda_agua_total numeric(18,2),
    consumo_energia_real numeric(18,3),
    emisiones_co2_real numeric(18,3),
    oferta_energia_real double precision
);


ALTER TABLE modelo_wefe.validacion_historica_mexico OWNER TO postgres;

--
-- Name: TABLE validacion_historica_mexico; Type: COMMENT; Schema: modelo_wefe; Owner: postgres
--

COMMENT ON TABLE modelo_wefe.validacion_historica_mexico IS 'Datos históricos de México para validación del modelo WEFE (2005-2020)';


--
-- Name: COLUMN validacion_historica_mexico.pib_real; Type: COMMENT; Schema: modelo_wefe; Owner: postgres
--

COMMENT ON COLUMN modelo_wefe.validacion_historica_mexico.pib_real IS 'Producto Interno Bruto en pesos constantes/reales';


--
-- Name: COLUMN validacion_historica_mexico.consumo_energia_real; Type: COMMENT; Schema: modelo_wefe; Owner: postgres
--

COMMENT ON COLUMN modelo_wefe.validacion_historica_mexico.consumo_energia_real IS 'Consumo de energía en Petajoules (PJ)';


--
-- Name: COLUMN validacion_historica_mexico.emisiones_co2_real; Type: COMMENT; Schema: modelo_wefe; Owner: postgres
--

COMMENT ON COLUMN modelo_wefe.validacion_historica_mexico.emisiones_co2_real IS 'Emisiones en millones de toneladas de CO2';


--
-- Data for Name: validacion_historica_mexico; Type: TABLE DATA; Schema: modelo_wefe; Owner: postgres
--

INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2005, 103263388, 18929250872000.00, 28000000.00, 10500000.00, 15000000.00, 5209580.00, 10032548.00, 472194.00, 76508.50, 4256.814, 447.289, 11511.889);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2006, 105078018, 19838803935000.00, 28500000.00, 10800000.00, 15500000.00, 5297680.00, 10252509.00, 465137.00, 77322.20, 4481.898, 463.912, 11492.891);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2007, 106892648, 20251027288000.00, 29000000.00, 11100000.00, 16000000.00, 5442649.00, 10828807.15, 458100.00, 78949.60, 4639.591, 470.842, 11003.923);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2008, 108707278, 20442061683000.00, 29500000.00, 11400000.00, 16500000.00, 5526809.26, 11077317.31, 459351.00, 79752.30, 4797.026, 472.266, 10729.036);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2009, 110521908, 19155182679000.00, 28000000.00, 11700000.00, 17000000.00, 5621725.00, 11035207.82, 460237.00, 80587.00, 4547.399, 461.546, 10461.401);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2010, 112336538, 20107450900000.00, 30000000.00, 12000000.00, 17500000.00, 5720122.00, 11163641.61, 462583.00, 80213.40, 4707.750, 476.923, 10264.637);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2011, 113775381, 20799960568000.00, 29000000.00, 12500000.00, 18000000.00, 5892444.00, 11212580.00, 471497.60, 81651.20, 4900.006, 486.519, 10274.736);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2012, 115214224, 21539027005000.00, 30500000.00, 13000000.00, 18500000.00, 5970635.00, 11367601.18, 471498.00, 82733.70, 4887.556, 506.226, 10011.447);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2013, 116653067, 21722561388000.00, 31000000.00, 13500000.00, 19000000.00, 6013374.00, 11451502.92, 471468.80, 81651.20, 4928.445, 494.013, 10018.198);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2014, 118091910, 22266442953000.00, 32000000.00, 14000000.00, 19500000.00, 6114712.00, 11623672.57, 447260.00, 84928.80, 4897.582, 480.816, 9568.301);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2015, 119530753, 22868154258000.00, 33000000.00, 14500000.00, 20000000.00, 6247882.00, 11900161.65, 446777.00, 85664.20, 5094.740, 490.301, 9224.298);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2016, 120827407, 23273490743000.00, 34000000.00, 15000000.00, 20500000.00, 6449428.77, 12121675.51, 450828.00, 86576.80, 5305.863, 496.335, 8812.59);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2017, 122124061, 23709107313000.00, 35000000.00, 15500000.00, 21000000.00, 6698151.00, 12287775.37, 451585.00, 87841.50, 5362.817, 500.557, 8241.716);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2018, 123420715, 24176670377000.00, 35500000.00, 15800000.00, 21500000.00, 6941611.62, 12534422.26, 451585.00, 88839.70, 5283.705, 476.057, 7654.463);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2019, 124717369, 24081730886000.00, 36000000.00, 16000000.00, 22000000.00, 7225537.56, 12810898.98, 456612.50, 89350.70, 4760.976, 485.265, 7364.643);
INSERT INTO modelo_wefe.validacion_historica_mexico (anio, poblacion_real, pib_real, prod_granos_real, prod_hortalizas_real, prod_frutas_real, prod_carne_real, prod_lacteos_real, oferta_agua_total, demanda_agua_total, consumo_energia_real, emisiones_co2_real, oferta_energia_real) VALUES (2020, 126014024, 22069934757000.00, 36500000.00, 16300000.00, 22500000.00, 7434160.22, 13109108.70, 461640.00, 89547.80, 4383.370, 427.815, 7057.538);


--
-- Name: validacion_historica_mexico validacion_historica_mexico_pkey; Type: CONSTRAINT; Schema: modelo_wefe; Owner: postgres
--

ALTER TABLE ONLY modelo_wefe.validacion_historica_mexico
    ADD CONSTRAINT validacion_historica_mexico_pkey PRIMARY KEY (anio);


--
-- PostgreSQL database dump complete
--

\unrestrict p8DfzQyD8DE2tHzyFUc4EDjap4JaD6GjUElTzeLheqwoYa7zwhtf6Yxqc7B6dns

