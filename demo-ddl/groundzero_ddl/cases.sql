
    create table action_rule (
       id uuid not null,
        classifiers bytea,
        has_triggered BOOLEAN DEFAULT false not null,
        trigger_date_time timestamp with time zone,
        primary key (id)
    );

    create table cases (
       id uuid not null,
        address_line1 varchar(255),
        metadata jsonb,
        msg_date_time timestamp,
        postcode varchar(255),
        primary key (id)
    );

    create table case_to_process (
       id  bigserial not null,
        batch_id uuid,
        batch_quantity int4 not null,
        action_rule_id uuid,
        caze_id uuid,
        primary key (id)
    );

    alter table if exists case_to_process 
       add constraint FKmqcrb58vhx7a7qcyyjjvm1y31 
       foreign key (action_rule_id) 
       references action_rule;

    alter table if exists case_to_process 
       add constraint FK104hqblc26y5xjehv2x8dg4k3 
       foreign key (caze_id) 
       references cases;
