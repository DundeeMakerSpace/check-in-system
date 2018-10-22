#include <nfc/nfc.h>
#include <cstdlib>
#include <cstring>
#include <algorithm>

static void print_hex(const uint8_t *pbtData, const size_t szBytes)
{
    size_t  szPos;

    printf("READ:");

    for (szPos = 0; szPos < szBytes; szPos++)
    {
        printf("%02x", pbtData[szPos]);
    }

    printf("\n");
    fflush(stdout);
}

int main(int argc, char **argv)
{
    nfc_device * pnd;
    nfc_target nt;

    nfc_context * context;

    nfc_init(&context);

    if (context == nullptr)
    {
        printf("ERROR: Unable to init libnfc (malloc)");
        exit(EXIT_FAILURE);
    }

    const char * acLibnfcVersion = nfc_version();

    //printf("%s uses libnfc %s\n", argv[0], acLibnfcVersion);

    pnd = nfc_open(context, nullptr);
    
    if (pnd == nullptr)
    {
        printf("ERROR: %s\n", "Unable to open NFC device");
        exit(EXIT_FAILURE);
    }

    if (nfc_initiator_init(pnd) < 0)
    {
        nfc_perror(pnd, "ERROR: nfc_initiator_init");
        exit(EXIT_FAILURE);
    }

    //printf("NFC reader: %s opened\n", nfc_device_get_name(pnd));

    const nfc_modulation nmMifare = {
        .nmt = NMT_ISO14443A,
        .nbr = NBR_106,
    };

    while (true)
    {
        if (nfc_initiator_select_passive_target(pnd, nmMifare, NULL, 0, &nt) > 0)
        {

            //printf("The following (NFC) ISO14443A tag was found:\n");
            //printf("    ATQA (SENS_RES): ");
            //print_hex(nt.nti.nai.abtAtqa, 2);
            //printf("       UID (NFCID%c): ", (nt.nti.nai.abtUid[0] == 0x08 ? '3' : '1'));
            //print_hex(nt.nti.nai.abtUid, nt.nti.nai.szUidLen);
            //printf("      SAK (SEL_RES): ");
            //print_hex(&nt.nti.nai.btSak, 1);

            uint64_t uniqueID = 0;

            if (nt.nti.nai.szAtsLen > 0)
            {
                // This is probably a phone.

                memcpy(&uniqueID,
                       nt.nti.nai.abtAts,
                       std::min(nt.nti.nai.szAtsLen, sizeof(uint64_t)));
            }
            else
            {
                // This is probably a fob or card.
                memcpy(&uniqueID,
                       nt.nti.nai.abtUid,
                       std::min(nt.nti.nai.szUidLen, sizeof(uint64_t)));
            }

            print_hex((uint8_t*)&uniqueID, sizeof(uint64_t));

            while (0 == nfc_initiator_target_is_present(pnd, nullptr)) {}
        }
    }


    nfc_close(pnd);
    nfc_exit(context);
    return 0;
}
