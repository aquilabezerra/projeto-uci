import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

@st.cache_data
def load_data(file_data):
    return pd.read_csv(file_data, sep=';')

# 🔹 Função para transformar DataFrame em Excel binário
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data


def multiselect_filter(df, col, selected):
    if 'all' in selected:
        return df
    else:
        return df[df[col].isin(selected)]


st.set_page_config(layout='wide', 
                   page_icon='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcEv36oHqvzkQXVoiF3YOCrQW0Wpm7a2duiA&s', 
                   page_title= 'Analisador de campanhas')


st.title("🎯 Analisador de Público-Alvo para Campanhas")

df = pd.read_csv("bank-additional-full.csv", sep=";")
st.write(df)

# Sidebar com filtros
st.sidebar.image('Bank-Branding.jpg')

st.sidebar.header("⚙️ Filtros")


# -- filtros adicionais --



with st.sidebar.form("filtros_form"):
    st.header("⚙️ Filtros")

    idade_min, idade_max = st.slider(
        "Selecione a faixa etária:",
        int(df['age'].min()),
        int(df['age'].max()),
        (30, 50)  # valor inicial
    )

# PROFISSÕES
    jobs_list = df.job.unique().tolist()
    jobs_list.append('all')
    jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

    # ESTADO CIVIL
    marital_list = df.marital.unique().tolist()
    marital_list.append('all')
    marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

    # DEFAULT?
    default_list = df.default.unique().tolist()
    default_list.append('all')
    default_selected = st.multiselect("Default", default_list, ['all'])

    # TEM FINANCIAMENTO IMOBILIÁRIO?
    housing_list = df.housing.unique().tolist()
    housing_list.append('all')
    housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

    # TEM EMPRÉSTIMO?
    loan_list = df.loan.unique().tolist()
    loan_list.append('all')
    loan_selected = st.multiselect("Tem empréstimo?", loan_list, ['all'])

    # MEIO DE CONTATO
    contact_list = df.contact.unique().tolist()
    contact_list.append('all')
    contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

    # MÊS DO CONTATO
    month_list = df.month.unique().tolist()
    month_list.append('all')
    month_selected = st.multiselect("Mês do contato", month_list, ['all'])

    # DIA DA SEMANA
    day_of_week_list = df.day_of_week.unique().tolist()
    day_of_week_list.append('all')
    day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

    # ✅ Botão aplicar (correto)
    submit_button = st.form_submit_button('Aplicar')



# Filtrar pela faixa etária escolhida
if submit_button:
    filtro = (
        df.query("age >= @idade_min and age <= @idade_max")
          .pipe(multiselect_filter, 'job', jobs_selected)
          .pipe(multiselect_filter, 'marital', marital_selected)
          .pipe(multiselect_filter, 'default', default_selected)
          .pipe(multiselect_filter, 'housing', housing_selected)
          .pipe(multiselect_filter, 'loan', loan_selected)
          .pipe(multiselect_filter, 'contact', contact_selected)
          .pipe(multiselect_filter, 'month', month_selected)
          .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
    )
else:
    filtro = df


st.subheader(f"📊 Resultados para idade entre {idade_min} e {idade_max} anos")

# Taxa de aceitação (target: 'y')
aceitaram = filtro[filtro['y'] == 'yes'].shape[0]
total = filtro.shape[0]
taxa = aceitaram / total * 100 if total > 0 else 0

st.write(f"- Pessoas na faixa etária: **{total}**")
st.write(f"- Aceitaram a oferta: **{aceitaram}**")
st.write(f"- Taxa de conversão: **{taxa:.2f}%**")

# 🔹 Gráfico atualizado com base no filtro
if total > 0:
    filtro['faixa_idade'] = pd.cut(filtro['age'], bins=range(10, 100, 10))
    conversao = filtro.groupby('faixa_idade')['y'].apply(lambda x: (x == 'yes').mean() * 100)

    fig, ax = plt.subplots(figsize=(15,5))
    conversao.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
    ax.set_ylabel("Taxa de Conversão (%)")
    ax.set_title("Conversão por Faixa Etária (filtrada)")
    st.pyplot(fig, use_container_width=True)
else:
    st.warning("Nenhum cliente nessa faixa etária.")


# 🔹 Botões para download
col1, col2 = st.columns(2)

df_xlsx = to_excel(df)
col1.write('### Proporção original')
col1.write(df)
col1.download_button(label='📥 Download',
                     data=df_xlsx,
                     file_name='bank_raw_y.xlsx')

# ⚠️ Aqui você usou 'bank_target_perc', mas ele não existe no código.
# Vou criar como exemplo: proporção do target filtrado
bank_target_perc = filtro['y'].value_counts(normalize=True).reset_index()
bank_target_perc.columns = ['y', 'proporcao']

df_xlsx = to_excel(bank_target_perc)
col2.write('### Proporção da tabela com filtros')
col2.write(bank_target_perc)
col2.download_button(label='📥 Download',
                     data=df_xlsx,
                     file_name='bank_y.xlsx')

st.markdown("---")