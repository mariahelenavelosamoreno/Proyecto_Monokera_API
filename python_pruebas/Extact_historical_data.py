def Extract_full_historical_load(**kwargs):
    ti = kwargs['ti']
    config = DEFAULT_CONFIG
    
    print("Iniciando extracción HISTÓRICA completa (one-time)")

    # 1. Cargar estado previo (si existe)
    state_file = config["STATE_FILE"]
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            last_offset = state.get("last_offset", 0)
            print(f"Offset inicial desde state.json: {last_offset}")
    except (FileNotFoundError, json.JSONDecodeError):
        last_offset = 0
        print("No se encontró state.json. Iniciando desde offset 0")

    # 2. Configuración de la extracción
    current_offset = last_offset  # Comienza desde el último offset conocido
    data = []
    extraction_active = True
    max_records = float('inf')  # Sin límite de registros

    # 3. Extracción paginada completa
    while extraction_active and len(data) < max_records:
        try:
            blogs = fetch_blogs(config["BASE_URL"], config["LIMIT"], current_offset)
            
            if not blogs:  # Fin de los datos
                print(" No hay más registros en la API")
                extraction_active = False
                break
                
            # Agregar datos y actualizar offset
            received = len(blogs)
            data.extend(blogs)
            current_offset += received
            
            # Actualizar estado en cada iteración (para resiliencia)
            with open(state_file, 'w') as f:
                json.dump({"last_offset": current_offset}, f)
            
            print(f" Lote recibido: {received} registros | Offset acumulado: {current_offset}")

            # Pequeño delay para evitar rate-limiting
            time.sleep(0.3)  
            
        except Exception as e:
            print(f" Error en extracción histórica: {str(e)}")
            # Conserva el último offset válido
            with open(state_file, 'w') as f:
                json.dump({"last_offset": current_offset}, f)
            raise

    # 4. Guardado de datos brutos
    if data:
        raw_df = pd.json_normalize(data)
        os.makedirs(config["RAW_DIR"], exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = f"{config['RAW_DIR']}/FULL_HISTORICAL_{timestamp}_blogs_raw.csv"
        
        try:
            raw_df.to_csv(output_file, sep=';', index=False)
            print(f"Extracción histórica completada. Total registros: {len(data)}")
            print(f"Archivo generado: {output_file}")

            # Actualizar estado final
            with open(state_file, 'w') as f:
                json.dump({"last_offset": current_offset, "last_execution": timestamp}, f)

            # Compartir metadatos
            ti.xcom_push(key='historical_raw_file', value=output_file)
            ti.xcom_push(key='total_records', value=len(data))
            
        except Exception as e:
            print(f"Error al guardar CSV histórico: {str(e)}")
            raise
    else:
        print("No se encontraron registros nuevos en la API")

    # 5. Log del estado final
    print("\n--- ESTADO FINAL ---")
    print(f"Último offset procesado: {current_offset}")
    print(f"Registros totales extraídos: {len(data)}")