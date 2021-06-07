create table Users (
    id_user int 
    , name text
    , surname text
    , password text
    , primary key (id_user)
);  

create table data1 (
    id_data INT
    , id_user INT
    , bpm int
    , time BIGINT
    , datasourse varchar
    , CONSTRAINT fk_users FOREIGN KEY(id_user)  REFERENCES Users(id_user)
    , primary key (id_data)
); 

create table Device (
    id_device INT
    , id_user INT
    , dtype TEXT
    , dmodel TEXT
    , description TEXT
    , token TEXT
    , CONSTRAINT fk_users FOREIGN KEY(id_user)  REFERENCES Users(id_user)
    , primary key (id_device)); 

CREATE TABLE Periods ( 
    id_period INT, 
    descr_eng text,  
    descr_local text, 
    PRIMARY KEY (id_period) 
);  

CREATE TABLE Settings (
    id_user INT
    , id_period INT
    , CONSTRAINT fk_settings1 FOREIGN KEY(id_user) REFERENCES Users(id_user)
    , CONSTRAINT fk_settings2 FOREIGN KEY(id_period) REFERENCES Periods(id_period)
);
