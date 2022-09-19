#!/usr/bin/env bash


. ./path.sh || exit 1;

if [ $# != 2 ]; then
  echo "Usage: $0 <corpus-path> <data-path>"
  echo " $0 /mnt/hdd18.2t/dataset/TCC300/tcc300 data/tcc300"
  exit 1;
fi
echo "$0 $@"

corpus=$1
datadir=$2

echo "**** Creating tcc300 data folder ****"

python local/tcc300_data_prep.py $corpus $datadir/all
./utils/fix_data_dir.sh $datadir/all

mv $datadir/all/text $datadir/all/text.raw

if [ ! -d chinese_text_normalization ]; then
    git clone https://github.com/kakushawn/chinese_text_normalization.git
  fi
python chinese_text_normalization/TN/cn_tn.py \
  --remove_punc true --has_key --to_upper $datadir/all/text.raw $datadir/all/text
gsed -i 's/ \+/ /g' $datadir/all/text

rm -rf $datadir/tmp && mkdir $datadir/tmp
tail -30 $datadir/all/spk2utt > $datadir/tmp/test_spk
head -10 $datadir/all/spk2utt > $datadir/tmp/dev_spk

ggrep -f $datadir/tmp/test_spk -v $datadir/all/spk2utt |
  ggrep -f $datadir/tmp/dev_spk -v > $datadir/tmp/train_spk

utils/subset_data_dir.sh --spk-list $datadir/tmp/test_spk $datadir/all $datadir/test
utils/subset_data_dir.sh --spk-list $datadir/tmp/dev_spk $datadir/all $datadir/dev
utils/subset_data_dir.sh --spk-list $datadir/tmp/train_spk $datadir/all $datadir/train

utils/data/validate_data_dir.sh --no-feats $datadir/test
utils/data/validate_data_dir.sh --no-feats $datadir/dev
utils/data/validate_data_dir.sh --no-feats $datadir/train
