from google.cloud import bigquery


def append_json_to_existing_table(json_filename, project_id, dataset_id, target_table_id, target_table_location):
    temp_table_id = "{}_temp_table".format(target_table_id)

    client = bigquery.Client()

    dataset_ref = bigquery.DatasetReference(project=project_id, dataset_id=dataset_id)
    table_ref = dataset_ref.table(table_id=temp_table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True

    with open(json_filename, "rb") as source_file:
        job = client.load_table_from_file(
            source_file,
            table_ref,
            location=target_table_location,
            job_config=job_config,
        )  # API request

    job.result()  # Waits for table load to complete.

    print("> loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, temp_table_id))

    # append temp table to target table

    # delete temp table
