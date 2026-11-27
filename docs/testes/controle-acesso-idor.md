# Testes de segurança — Controle de acesso e IDOR

**Data:** 26/11/2026  
**Projeto:** SACP  
**Ambiente:** aplicação local com Flask e PostgreSQL

## Objetivo

Testei se cada perfil consegue acessar somente as funcionalidades e informações permitidas. Usei as contas de administrador, recepção e líder, tanto pela navegação normal quanto digitando os endereços diretamente no navegador. Também conferi se o líder consegue visualizar registros atribuídos a outros responsáveis.

## Resumo

| Verificação | Resultado inicial | Resultado final |
| --- | --- | --- |
| Acesso direto às páginas restritas | Aprovado | Aprovado |
| Informações pastorais no cadastro de Pessoas | Falhou | Aprovado |
| Permissões do perfil Líder | Aprovado nas rotas gerais | Aprovado |
| Visualização de acompanhamentos e tarefas por responsável | Precisava de restrição | Aprovado |
| Acesso direto a registros de outro responsável (IDOR) | — | Aprovado |
| Dashboard do Líder | Precisava de filtro por responsável | Aprovado |
| Botões de criação nas listagens do Líder | Apareciam, mas retornavam 403 | Aprovado |

## SEC-04 — Acesso às páginas conforme o perfil

Primeiro, entrei com a conta de recepção e tentei acessar diretamente os módulos pela URL. A página de Pessoas abriu normalmente, mas Acompanhamentos, Tarefas, Pequenos Grupos, Discipulados, EBD, Pedidos de Oração, Relatórios e Usuários retornaram **403**, como esperado.

Depois conferi as permissões gerais do perfil Líder. O acesso às páginas permitidas funcionou, e as operações restritas continuaram bloqueadas.

**Resultado:** as rotas testadas respeitaram as permissões de cada perfil. **Aprovado.**

## SEC-04 — Informações pastorais no perfil da pessoa

Em seguida, abri o cadastro de uma pessoa usando a conta de recepção. Mesmo sem permissão para acessar os módulos de Acompanhamentos e Tarefas, a recepção conseguia visualizar essas informações dentro da página de detalhes da pessoa.

Isso era um problema porque esconder o acesso aos módulos não impedia que dados pastorais aparecessem em outra página. Aproveitei para revisar também a opção de inativar ou reativar cadastros, que deve ficar disponível somente para administrador e pastoral.

**Correção:** ajustei as consultas e o template de detalhes de Pessoas para separar as informações mostradas conforme o perfil. A recepção passou a visualizar somente os dados cadastrais, e os botões de inativar e reativar ficaram restritos a administrador e pastoral. As rotas dessas ações já estavam protegidas no backend.

**Reteste:** entrei novamente como recepção e abri o perfil de uma pessoa. Os dados pastorais e os botões de inativação não apareceram. **Aprovado.**

## SEC-04 — Acompanhamentos e tarefas atribuídos ao Líder

Também revisei o acesso do Líder. Antes dessa etapa, as permissões eram definidas principalmente pelo perfil, sem limitar a visualização dos acompanhamentos e tarefas ao usuário responsável por cada registro.

Decidi que, por enquanto, o Líder poderá **consultar apenas acompanhamentos e tarefas atribuídos a ele**, enquanto criação, edição, encerramento e conclusão ficam com administrador e pastoral.

**Correção:** adicionei filtros pelo campo `responsavel_id` nas consultas de Acompanhamentos e Tarefas. Os mesmos filtros foram aplicados às informações que aparecem no perfil de Pessoas. Também ajustei a autorização das rotas para impedir alterações pelo Líder.

**Reteste:** acessei uma pessoa que tinha registros atribuídos a responsáveis diferentes. Com a conta de Líder, apareceram somente os acompanhamentos e tarefas atribuídos àquela conta. O administrador continuou conseguindo consultar e gerenciar os registros normalmente. **Aprovado.**

## SEC-04.1 — Acesso direto a registros de outro responsável (IDOR)

Para conferir se o filtro não funcionava apenas nas listagens, entrei como administrador e copiei os endereços de um acompanhamento e de uma tarefa atribuídos a outro usuário. Depois tentei abrir esses mesmos endereços com a conta de Líder.

Também testei os endereços de edição dos registros.

**Resultado:** o sistema retornou **403** ao tentar acessar ou editar registros que não estavam atribuídos ao Líder. **Aprovado.**

## SEC-04.2 — Dashboard do Líder

Depois, conferi a página inicial com a conta de Líder. Verifiquei os indicadores de acompanhamentos ativos, tarefas pendentes e atrasadas, além das listas de registros recentes e que precisam de atenção.

**Correção:** as consultas do dashboard foram ajustadas para considerar somente os registros atribuídos ao usuário quando o perfil é Líder.

**Reteste:** os números e as listas passaram a mostrar apenas os acompanhamentos e tarefas atribuídos à conta utilizada. **Aprovado.**

## SEC-04 — Botões de criação nas listagens

Por último, percebi que os botões **Novo acompanhamento** e **Nova tarefa** ainda apareciam nas páginas de listagem para o Líder. Ao clicar, o sistema já retornava 403, então a restrição do backend estava funcionando. Mesmo assim, não fazia sentido mostrar uma ação que o perfil não pode executar.

**Correção:** ajustei os templates das listagens para exibir esses botões somente para administrador e pastoral.

**Reteste:** os botões deixaram de aparecer para o Líder, mas continuaram disponíveis para os perfis autorizados. As URLs de criação permaneceram protegidas. **Aprovado.**

## Conclusão

Os testes confirmaram que as principais rotas já tinham restrições por perfil, mas mostraram uma falha na página de detalhes de Pessoas: a recepção conseguia visualizar informações pastorais sem ter acesso aos módulos correspondentes.

Corrigi essa exposição e implementei a visualização de Acompanhamentos e Tarefas por responsável para o perfil Líder. Também conferi o acesso direto por ID, os dados do dashboard e os botões da interface. Após os ajustes, todos os retestes realizados nesta etapa foram aprovados.

O controle individual por responsável foi aplicado **a Acompanhamentos e Tarefas**. As permissões de Pequenos Grupos, Discipulados e EBD continuam seguindo as regras próprias desses módulos.
