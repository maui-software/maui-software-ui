import pandas as pd
import numpy as np
import json
import pyarrow as pa
import pyarrow.parquet as pq

def convert_to_serializable(obj):
    """
    Converte objetos numpy para tipos nativos Python (lista, float, int).
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    else:
        return obj

def is_complex_list_array(val):
    """
    Retorna True se é lista, dict, tuple ou numpy.ndarray — objetos compostos.
    """
    return isinstance(val, (list, dict, tuple, np.ndarray))

def is_numpy_scalar(val):
    """
    Retorna True se é um numpy escalar (np.float64, np.int32, etc).
    """
    return isinstance(val, (np.generic,)) and not isinstance(val, np.ndarray)

def save_df_complex_parquet(df: pd.DataFrame, path: str):


    df_copy = df.copy()
    complex_cols = []
    
    for col in df_copy.columns:
        col_series = df_copy[col]
        # Se coluna tem lista, array ou dict em alguma célula: serializa JSON (string)
        if col_series.apply(is_complex_list_array).any():
            df_copy[col] = col_series.apply(lambda x: json.dumps(convert_to_serializable(x)))
            complex_cols.append(col)
        # Se coluna tem só escalares numpy, converte pra float/int (tipo nativo)
        elif col_series.apply(is_numpy_scalar).any():
            # Converte toda a série para tipos nativos para evitar salvar como string
            df_copy[col] = col_series.apply(convert_to_serializable)
        # Caso contrário, deixa como está (tipo simples já suportado)
    
    table = pa.Table.from_pandas(df_copy)
    metadata = table.schema.metadata or {}
    metadata = dict(metadata)
    # Salva quais colunas foram serializadas para JSON (complexas)
    metadata[b'complex_cols'] = json.dumps(complex_cols).encode()
    table = table.replace_schema_metadata(metadata)
    
    pq.write_table(table, path)

def load_df_complex_parquet(path: str) -> pd.DataFrame:
    table = pq.read_table(path)
    metadata = table.schema.metadata or {}
    complex_cols = json.loads(metadata.get(b'complex_cols', b'[]').decode())
    df = table.to_pandas()
    # Desserializa colunas complexas que estavam como JSON string
    for col in complex_cols:
        df[col] = df[col].apply(json.loads)
    return df
