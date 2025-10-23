# План разработки MGC Audits Backend

## Подготовка проекта

1. Создать структуру директорий backend приложения
2. Создать файл requirements.txt с базовыми зависимостями
3. Создать файл .env.example с переменными окружения
4. Создать файл pyproject.toml для настройки проекта
5. Настроить gitignore для Python проекта
6. Создать docker-compose.yml с сервисами PostgreSQL, Redis и backend
7. Создать Dockerfile для backend приложения
8. Создать Makefile с командами для управления проектом
9. Создать директорию app/ с базовой структурой модулей
10. Создать main.py с базовой конфигурацией FastAPI и автоматической генерацией Swagger
11. Создать core/config.py для настроек приложения
12. Создать core/security.py для функций безопасности
13. Создать database.py для подключения к PostgreSQL через SQLAlchemy
14. Создать core/base.py с AbstractBaseModel и SoftDeleteMixin
15. Настроить Alembic для миграций базы данных
16. Создать init_db.py для инициализации базы данных

## Базовые модели и пользователи

17. Создать модель Enterprise в models/enterprise.py
18. Создать модель Division в models/division.py
19. Создать модель Location в models/location.py
20. Создать модель User в models/user.py
21. Создать модели Role и Permission в models/role.py
22. Создать модель UserRole в models/user_role.py
23. Создать схемы Pydantic для User в schemas/user.py
24. Создать схемы Pydantic для Enterprise в schemas/enterprise.py
25. Создать CRUD операции для User в crud/user.py
26. Создать CRUD операции для Enterprise в crud/enterprise.py
27. Создать CRUD операции для Role в crud/role.py
28. Создать API роуты для User в api/users.py
29. Создать API роуты для Enterprise в api/enterprises.py
30. Создать API роуты для Role в api/roles.py

## Авторизация и аутентификация

31. Реализовать функцию генерации JWT токенов в core/security.py
32. Реализовать функцию проверки пароля в core/security.py
33. Создать эндпоинт POST /api/v1/auth/login
34. Создать эндпоинт POST /api/v1/auth/refresh
35. Создать эндпоинт POST /api/v1/auth/logout
36. Создать эндпоинт POST /api/v1/auth/register
37. Создать middleware для проверки JWT токенов
38. Создать middleware для проверки RBAC прав
39. Реализовать LDAP подключение в services/ldap.py
40. Создать эндпоинт для LDAP авторизации
41. Реализовать OTP генерацию в services/otp.py
42. Создать эндпоинт POST /api/v1/auth/otp/generate
43. Создать эндпоинт POST /api/v1/auth/otp/verify
44. Реализовать механизм единой сессии
45. Создать модель RegistrationInvite
46. Создать CRUD для RegistrationInvite
47. Создать эндпоинт для создания приглашений
48. Реализовать отправку email с приглашением

## Telegram интеграция

49. Создать модель APIToken в models/api_token.py
50. Создать CRUD для APIToken
51. Создать эндпоинт POST /api/v1/auth/telegram/link
52. Создать эндпоинт POST /api/v1/auth/telegram/unlink
53. Реализовать Telegram бота в services/telegram.py
54. Создать обработчик команд бота

## Workflow и статусы

55. Создать модель Status в models/status.py
56. Создать модель StatusTransition в models/status_transition.py
57. Создать схемы для Status
58. Создать схемы для StatusTransition
59. Создать CRUD для Status
60. Создать CRUD для StatusTransition
61. Создать API роуты для workflow/statuses
62. Создать API роуты для workflow/transitions
63. Реализовать валидацию переходов статусов
64. Реализовать проверку required_fields при смене статуса
65. Реализовать проверку required_roles при смене статуса

## Справочники

66. Создать модель DictionaryType в models/dictionary.py
67. Создать модель Dictionary в models/dictionary.py
68. Создать модели для конкретных справочников (Process, Norm, Product, Project, Client, Shift, RiskLevel, AuditCategory)
69. Создать схемы для Dictionary
70. Создать CRUD для Dictionary
71. Создать API роуты для dictionaries
72. Создать API роуты для dictionary_types
73. Реализовать фильтрацию справочников по enterprise_id

## Планирование аудитов

74. Создать модель AuditPlan в models/audit_plan.py
75. Создать модель AuditPlanItem в models/audit_plan_item.py
76. Создать схемы для AuditPlan
77. Создать схемы для AuditPlanItem
78. Создать CRUD для AuditPlan
79. Создать CRUD для AuditPlanItem
80. Создать API роуты для audit_plans
81. Создать API роуты для audit_plan_items
82. Реализовать логику согласования плана на уровне Дивизиона
83. Реализовать логику согласования плана на уровне УК
84. Создать эндпоинт POST /api/v1/audit_plans/{id}/approve_by_division
85. Создать эндпоинт POST /api/v1/audit_plans/{id}/approve_by_uk
86. Создать эндпоинт POST /api/v1/audit_plans/{id}/reject

## Квалификация аудиторов

87. Создать модель AuditorQualification в models/auditor_qualification.py
88. Создать модель QualificationStandard в models/qualification_standard.py
89. Создать модель StandardChapter в models/standard_chapter.py
90. Создать M2M связь между AuditorQualification и QualificationStandard
91. Создать схемы для AuditorQualification
92. Создать CRUD для AuditorQualification
93. Создать API роуты для auditor_qualifications
94. Реализовать проверку квалификации при назначении аудитора
95. Создать фоновую задачу для автоматического изменения статуса expired

## Аудиты

96. Создать модель Audit в models/audit.py
97. Создать модель AuditComponent в models/audit_component.py
98. Создать модель AuditScheduleWeek в models/audit_schedule_week.py
99. Создать M2M таблицы для AuditLocations, AuditClients, AuditShifts
100. Создать схемы для Audit
101. Создать схемы для AuditComponent
102. Создать схемы для AuditScheduleWeek
103. Создать CRUD для Audit
104. Создать CRUD для AuditComponent
105. Создать CRUD для AuditScheduleWeek
106. Создать API роуты для audits
107. Создать API роуты для audit_components
108. Реализовать фильтрацию аудитов по категориям
109. Реализовать эндпоинт GET /api/v1/audits/calendar/schedule
110. Реализовать логику автоматического заполнения ячеек графика
111. Реализовать эндпоинт PATCH /api/v1/audits/{audit_id}/schedule/{week_number}/{year}
112. Реализовать эндпоинт GET /api/v1/audits/calendar/by_component
113. Реализовать эндпоинт POST /api/v1/audits/{id}/reschedule
114. Реализовать эндпоинт GET /api/v1/audits/{id}/reschedule_history
115. Реализовать логику переносов аудитов
116. Реализовать вычисление color для ячеек графика

## Несоответствия (Findings)

117. Создать модель Finding в models/finding.py
118. Создать модель FindingDelegation в models/finding_delegation.py
119. Создать модель FindingComment в models/finding_comment.py
120. Создать схему для Finding
121. Создать схему для FindingDelegation
122. Создать схему для FindingComment
123. Создать CRUD для Finding
124. Создать CRUD для FindingDelegation
125. Создать CRUD для FindingComment
126. Создать API роуты для findings
127. Создать API роуты для finding_delegations
128. Создать API роуты для finding_comments
129. Реализовать валидацию полей для CAR1
130. Реализовать валидацию полей для CAR2
131. Реализовать валидацию полей для OFI
132. Реализовать логику делегирования responsibility
133. Реализовать автоинкремент finding_number

## Вложения

134. Создать модель Attachment в models/attachment.py
135. Создать схемы для Attachment
136. Создать CRUD для Attachment
137. Создать API роуты для attachments
138. Реализовать загрузку файлов в Yandex Object Storage
139. Реализовать pre-signed URLs для доступа к файлам
140. Реализовать полиформическую связь Attachment с сущностями

## История изменений

141. Создать модель ChangeHistory в models/change_history.py
142. Создать схемы для ChangeHistory
143. Создать CRUD для ChangeHistory
144. Создать API роуты для change_history
145. Реализовать автоматическое логирование изменений в Audit
146. Реализовать автоматическое логирование изменений в Finding
147. Создать эндпоинт GET /api/v1/audits/{id}/history
148. Создать эндпоинт GET /api/v1/findings/{id}/history

## Уведомления

149. Создать модель Notification в models/notification.py
150. Создать модель NotificationQueue в models/notification_queue.py
151. Создать схемы для Notification
152. Создать схемы для NotificationQueue
153. Создать CRUD для Notification
154. Создать CRUD для NotificationQueue
155. Создать сервис для отправки Email в services/email.py
156. Создать сервис для отправки Telegram в services/telegram_notify.py
157. Настроить Celery для фоновых задач
158. Создать Celery задачу для батчевой отправки Email
159. Создать Celery задачу для батчевой отправки Telegram
160. Реализовать retry механизм с логированием ошибок
161. Создать API роуты для notifications
162. Создать эндпоинт GET /api/v1/notifications/stats
163. Создать API роуты для администрирования очередей
164. Реализовать уведомление при создании finding
165. Реализовать уведомление при изменении статуса
166. Реализовать уведомление при приближении deadline
167. Реализовать уведомление при просрочке deadline
168. Реализовать уведомление при делегировании
169. Реализовать уведомление при добавлении комментария

## Настройки системы

170. Создать модель SystemSetting в models/system_setting.py
171. Создать схемы для SystemSetting
172. Создать CRUD для SystemSetting
173. Создать API роуты для settings
174. Реализовать шифрование значений для критичных настроек
175. Создать сервис для работы с S3 в services/s3.py
176. Создать модель S3Storage в models/s3_storage.py
177. Создать модель EmailAccount в models/email_account.py
178. Создать модель LdapConnection в models/ldap_connection.py
179. Создать CRUD для S3Storage
180. Создать CRUD для EmailAccount
181. Создать CRUD для LdapConnection
182. Создать API роуты для integrations/s3_storages
183. Создать API роуты для integrations/email_accounts
184. Создать API роуты для integrations/ldap_connections
185. Реализовать эндпоинт POST /api/v1/integrations/s3_storages/{id}/test
186. Реализовать эндпоинт POST /api/v1/integrations/email_accounts/{id}/test
187. Реализовать эндпоинт POST /api/v1/integrations/ldap_connections/{id}/test

## API токены

188. Создать CRUD для APIToken
189. Создать API роуты для api_tokens
190. Реализовать генерацию токенов
191. Реализовать хеширование токенов
192. Реализовать ротацию токенов
193. Реализовать проверку IP whitelist
194. Реализовать режим inherit permissions
195. Реализовать режим custom permissions

## Dashboard

196. Создать API роуты для dashboard
197. Реализовать эндпоинт GET /api/v1/dashboard/stats
198. Реализовать эндпоинт GET /api/v1/dashboard/my_tasks
199. Реализовать подсчет активных findings пользователя
200. Реализовать подсчет предстоящих аудитов пользователя
201. Реализовать общую статистику системы

## Отчеты

202. Создать API роуты для reports
203. Реализовать эндпоинт GET /api/v1/reports/findings
204. Реализовать эндпоинт GET /api/v1/reports/by_processes
205. Реализовать эндпоинт GET /api/v1/reports/by_solvers
206. Реализовать экспорт отчета findings в Excel
207. Реализовать экспорт отчета by_processes в Excel
208. Реализовать экспорт отчета by_solvers в Excel
209. Реализовать фильтрацию для отчетов
210. Реализовать сортировку для отчетов

## Экспорт данных аудита

211. Создать сервис для экспорта аудита в services/export.py
212. Реализовать сбор данных аудита
213. Реализовать сбор связанных findings
214. Реализовать сбор вложений
215. Реализовать сбор истории изменений
216. Реализовать упаковку в ZIP архив
217. Создать эндпоинт POST /api/v1/audits/{id}/export
218. Создать Celery задачу для асинхронного экспорта

## Документация

219. Создать README для проекта
220. Создать инструкцию по установке
221. Создать инструкцию по развертыванию
222. Создать документацию по API

## Финальная проверка

223. Провести code review кода
224. Исправить найденные баги
225. Проверить работу всех интеграций
226. Проверить работу уведомлений
227. Проверить работу отчетов
228. Подготовить к деплою на PROD
229. Развернуть на PROD сервере
230. Провести финальное тестирование на PROD
