# Analise-de-Imagens
Analisar imagens digitais via hurts e Binarizacao



Utilizando o Programa

Primeiramente, acesse o repositório GitHub no link . Baixe a pasta "Prototipo". Em seguida, leia o arquivo de texto que explica como compilar o script e instalar as bibliotecas necessárias para executar o programa. Após instalar as dependências, navegue até o local do arquivo executável e abra o terminal.

Execute o programa utilizando o comando: python3 i.py

Após a compilação, uma interface gráfica será exibida.

No campo "Nome da Propriedade", insira o nome da propriedade analisada (exemplo: Rugosidade). No campo "Valor da Propriedade", insira o valor correspondente obtido experimentalmente. Selecione o tipo de análise desejada. No exemplo, selecionaremos "Limiar e Cálculo do Expoente de Hurst".

Clique no botão "Selecionar Imagem".



Uma janela será aberta para você selecionar a imagem a ser analisada. A imagem deve estar em formato JPEG, PNG ou BMP.

Após a seleção da imagem, o histograma será exibido. Ao fechá-lo, o gráfico de Hurst será apresentado. Ao fechar o gráfico, o programa criará pastas de saída contendo a imagem binarizada (pelo limiar), o gráfico de Hurst, e exibirá na tela os valores de saturação do método utilizado, os valores de B, D, b/d e o valor médio de Hurst.


No exemplo, foram analisadas 7 amostras. Para gerar o gráfico b/d vs Propriedade, clique no botão correspondente. Observe que o programa só gera gráficos se o mesmo limiar for utilizado para todas as amostras.


