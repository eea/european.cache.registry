**Syncronize multi year licences**

Firstly, multi year licences syncronization and aggregation depends on having the substances, combined nomenclature and detailed uses defined in European Cache Registry.

To import (or update) this information, if it is not available, please run the following commands:

* Import both the substances and combined nomenclature.

        python -m flask sync import_combined_nomenclature


* Import detailed uses. You will notice that the detailed uses with *No reporting obligation* are not imported. They were added to this file only to be used if there is a case in which we receive this obligation and we receive a warning that the obligation does not exist in our database.

        python -m flask sync import_detailed_uses


After the metadata is imported in European cache registry, we can ahead and fetch the information for Multi Year Licences.
This information is fetched from 2 separate endpoints using 2 different commands. They need to be run in the order below, as `sync certex_quantities` depends on the information fetched and aggregated in `sync multi_year_licences`.

* Import Multi Year licences

  The first command, `sync multi_year_licences` brings all the Multi year licences that were valid in the given year. Please mind that those licences will be valid for multiple year, but the command will aggregate information only for the given year.

  The endpoint also receives parameters for receiving only information regarding one company's licences or a specific licence. However, the commands does not allow sync for partial data, as the
  aggregation depends on all data for a given year.
   
        python -m flask sync multi_year_licences [-y 2025] [-p 200]

* Import Certex information

  After running `sync multi_year_licences`, you can complete the multi year licence information pulling quantity data from Certex. This command will pull all quantities information available and grouped by MRN and licence, providing also information about the custom procedures.

  Same as above, the endpoint would allow fetching only information related to one company, but for simplification of the aggregation, this is not currently allowed. The command also
  can receive a --from_data and --to_date parameters. This will restrict the period between which the information is pulled and aggregated for a year. Those parameters are not however mandatory, as on receiving the mandatory year parameter, the information is pulled from 01.01.[year] to 31.12.[year] (with an exception for 2025).
    
       python -m flask sync certex_quantities -y [--year 2025] -fd [--from_date 01012025] -td [--to_date 31122025] -o [--offset 200] -p [--page_size 200]


For patching licences, set `PATCH_MULTI_YEAR_LICENCES` to a list of licences to be added to
a licences/aggregated endpoint. Only the data for the company_id and the given year will
be patched.
