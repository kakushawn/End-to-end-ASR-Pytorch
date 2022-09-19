import sys
import glob
import os

campus2wavprefix = {
    'NCTU' : '01',
    'NTHU' : '02',
    'NTU' : '03'
}

wav_path_format = "{}/WAV/{}/{}.wav"
wav_scp_format = "{} sox -t wav {} -r 16000 -b 16 -c 1 -t wav - |\n"

def main(corpus, datadir):
    global wav_path_format
    utts = []
    for campus in ['NCTU', 'NTU', 'NTHU']:
        for f in glob.glob("{}/{}/**/*.TAB".format(corpus, campus)):
            group, tab = f.split("/")[-2:]

            spk = "{}_{}{}".format(
                group.upper(),
                campus2wavprefix[campus],
                tab.split(".")[0][-6:-4])
            spk_id = "TCC300_{}".format(spk)

            with open(f, "r", encoding='big5hkscs') as fp:
                fp.readline().strip("\n")

                wav_name = "M{}{}".format(campus2wavprefix[campus], tab.split(".")[0][-6:])
                utt_id = "TCC300_{}_{}".format(spk, wav_name)
                #utt_id = wav_name+".wav"

                wav_path = wav_path_format.format(corpus, group, wav_name)

                counter = 0
                segs = []
                for line in fp:
                    if counter == 0:
                        seg = {}
                        segseq, beg, dur = line.strip("\n").split(" ")[0:3]
                        segid = "{}_{:03d}".format(utt_id, int(segseq))
                        beg = float(beg)/100
                        dur = float(dur)/100
                        seg = {"id":segid, "beg":beg, "dur":dur}
                        counter += 1
                    elif counter == 1:
                        text = line.strip("\n")
                        seg["text"] = text
                        segs.append(seg)
                        counter += 1
                    elif counter == 2:
                        counter += 1
                    else:
                        text = line.strip("\n")
                        counter = 0

            utt = {
                "wav_path": wav_path,
                "segments": segs,
                "spk_id": spk_id,
                "id": utt_id
            }
            utts.append(utt)

    if os.path.exists(datadir):
        import shutil
        shutil.rmtree(datadir)
    os.makedirs(datadir)
    with open(datadir+"/text", "w", encoding="utf-8") as fp_text, \
        open(datadir+"/segments", "w", encoding="utf-8") as fp_segments, \
        open(datadir+"/wav.scp", "w", encoding="utf-8") as fp_wavscp, \
        open(datadir+"/utt2spk", "w", encoding="utf-8") as fp_utt2spk:
        for utt in utts:
            for segment in utt['segments']:
                line_text = "{} {}\n".format(segment["id"], segment["text"])
                fp_text.write(line_text)
                line_segments = "{} {} {} {}\n".format(
                    segment["id"],
                    utt["id"],
                    "{:3.2f}".format(segment["beg"]),
                    "{:3.2f}".format(segment["beg"]+segment["dur"]),
                )
                fp_segments.write(line_segments)
                line_utt2spk =  "{} {}\n".format(segment["id"], utt["spk_id"])
                fp_utt2spk.write(line_utt2spk)
            fp_wavscp.write(wav_scp_format.format(utt['id'], utt['wav_path']))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage python {} /mnt/hdd18.2t/dataset/TCC300/tcc300 data/tcc300\n".format(sys.argv[0]))
        sys.exit(1)

    _, corpus, datadir = sys.argv[:]

    main(corpus=corpus, datadir=datadir)
