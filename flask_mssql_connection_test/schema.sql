-- Create employees table (company_db)
IF OBJECT_ID('dbo.employees', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.employees (
        id         INT IDENTITY(1,1)    NOT NULL,
        name       NVARCHAR(100)        NOT NULL,
        department NVARCHAR(100)        NOT NULL,
        salary     DECIMAL(12,2)        NOT NULL,
        created_at DATETIME2            NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_employees PRIMARY KEY CLUSTERED (id)
    );
END
GO