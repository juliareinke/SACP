# Testes de segurança — Autenticação e sessões

**Data:** 25/11/2026  
**Projeto:** SACP  
**Ambiente:** aplicação local com Flask e PostgreSQL

## Objetivo

Testei como o SACP lida com usuários desativados e com sessões que já estavam abertas. Para isso, usei duas janelas: uma com o administrador e outra, anônima, com a conta **Recepção Teste**.

## Resumo

| Teste | O que foi verificado | Resultado inicial | Resultado final |
| --- | --- | --- | --- |
| SEC-01 | Acesso de usuário desativado | Falhou | Aprovado |
| SEC-02 | Sessão antiga depois de reativar a conta | Falhou | Aprovado |
| SEC-03 | Sessão antiga após troca de senha | — | Aprovado |

## SEC-01 — Usuário desativado

Primeiro, entrei com a conta de recepção e, em outra janela, desativei esse usuário pelo administrador. Mesmo desativada, a recepção continuou conseguindo abrir Pessoas, voltar ao dashboard e navegar normalmente.

O problema estava na forma como a sessão era carregada: o sistema não conferia corretamente se o usuário ainda estava ativo.

**Correção:** alterei o `user_loader` em `app/__init__.py` para não carregar contas inativas e adicionei a propriedade `is_active` ao modelo `Usuario`, usando o campo `ativo` do banco.

**Reteste:** quando tentei acessar Pessoas com a conta desativada, fui redirecionada ao login. Também não consegui entrar novamente enquanto ela permanecia inativa. **Aprovado.**

## SEC-02 — Sessão antiga após reativação

Depois da primeira correção, fiz outro teste: desativei a conta, confirmei que o acesso havia sido bloqueado e então a reativei. Ao abrir Pessoas sem fazer um novo login, a sessão antiga voltou a funcionar.

Ou seja, verificar apenas se a conta estava ativa não era suficiente para invalidar a sessão anterior.

**Correção:** adicionei o campo `versao_sessao` ao modelo `Usuario` e gerei uma migration. Também ajustei `get_id()` e `user_loader` para conferir essa versão. Ao desativar uma conta, a versão é incrementada, fazendo com que as sessões antigas deixem de ser aceitas.

**Reteste:** após desativar e reativar a conta, não foi possível reutilizar a sessão anterior. Foi necessário entrar novamente. **Aprovado.**

## SEC-03 — Alteração de senha

Por último, testei a troca de senha pelo administrador. Mantive a conta de recepção conectada em outra janela, alterei sua senha e tentei continuar navegando com a sessão antiga.

Nesse caso, o sistema já estava configurado para incrementar `versao_sessao` quando a senha fosse alterada.

**Resultado:** a sessão antiga perdeu o acesso, a senha anterior deixou de funcionar e consegui entrar com a nova senha. **Aprovado.**

## Conclusão

Os testes mostraram duas falhas no controle de sessões, que foram corrigidas e testadas novamente. Com as alterações, contas desativadas não conseguem continuar acessando o sistema, sessões anteriores à desativação não voltam a funcionar após a reativação e a troca de senha também invalida sessões antigas.
