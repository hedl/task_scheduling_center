-- auto-generated definition
create table task_queue
(
    id          bigint unsigned auto_increment comment '主键ID'
        primary key,
    task_name   varchar(255)                               not null comment '任务名称',
    task_type   varchar(50)                                null comment '任务类型',
    task_state  tinyint unsigned default '0'               not null comment '任务状态：0-待执行，1-执行中，2-成功，3-失败，4-取消',
    start_time  datetime                                   null comment '开始执行时间',
    finish_time datetime                                   null comment '完成执行时间',
    task_param  json                                       null comment '任务执行参数（查询条件）',
    error_msg   text                                       null comment '错误信息',
    remark_json json                                       null comment '其他备注信息（JSON格式）',
    create_date datetime         default CURRENT_TIMESTAMP not null comment '创建时间',
    update_date datetime         default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间'
)
    comment '任务队列表' collate = utf8mb4_unicode_ci;

create index idx_create_date
    on task_queue (create_date);

create index idx_state_create
    on task_queue (task_state, create_date);

create index idx_task_state
    on task_queue (task_state);

create index idx_task_type
    on task_queue (task_type);

