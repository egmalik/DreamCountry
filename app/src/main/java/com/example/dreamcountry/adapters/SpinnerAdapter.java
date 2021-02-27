package com.example.dreamcountry.adapters;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.drawable.PictureDrawable;
import android.net.Uri;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import com.bumptech.glide.GenericRequestBuilder;
import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.bumptech.glide.load.model.StreamEncoder;
import com.bumptech.glide.load.resource.file.FileToStreamDecoder;
import com.caverock.androidsvg.SVG;
import com.example.dreamcountry.R;
import com.example.dreamcountry.SVGparser.SvgDecoder;
import com.example.dreamcountry.SVGparser.SvgDrawableTranscoder;
import com.example.dreamcountry.SVGparser.SvgSoftwareLayerSetter;
import com.example.dreamcountry.model.Country;

import java.io.InputStream;
import java.util.List;

// Creating an Adapter Class
public class SpinnerAdapter extends ArrayAdapter {
    private boolean firsttime = true;
    private TextView countryName ;
    private TextView countryarea ;
    private ImageView countryflag ;

    private List<Country> countryList;
    private Context context ;


    public SpinnerAdapter(Context context, int textViewResourceId, List<String> objects , List<Country> countryList) {
        super(context, textViewResourceId, objects);
        this.context = context ;
        this.countryList = countryList;
    }

    public View getCustomView(int position, View convertView, ViewGroup parent) {
        LayoutInflater inflater = LayoutInflater.from(context);
        View layout = inflater.inflate(R.layout.country_item, parent, false);
        attachView(layout);
        if (position==0) {
           // countryflag.setVisibility(View.INVISIBLE);
            countryarea.setVisibility(View.INVISIBLE);
        }
        if (countryList.get(position).getArea()==null) countryList.get(position).setArea((float)0);
        countryName.setText(countryList.get(position).getName()+ " - " + countryList.get(position).getNativeName());
        countryarea.setText(countryList.get(position).getArea().doubleValue()+ " -area");
        fillImg(position);
        return layout;
    }

    private void fillImg(int position) {
        int wid = Resources.getSystem().getDisplayMetrics().widthPixels;
        GenericRequestBuilder<Uri, InputStream, SVG, PictureDrawable> requestBuilder = Glide.with(context)
                .using(Glide.buildStreamModelLoader(Uri.class, context), InputStream.class)
                .from(Uri.class)
                .as(SVG.class)
                .transcode(new SvgDrawableTranscoder(), PictureDrawable.class)
                .sourceEncoder(new StreamEncoder())
                .cacheDecoder(new FileToStreamDecoder<SVG>(new SvgDecoder()))
                .decoder(new SvgDecoder())
                .listener(new SvgSoftwareLayerSetter<Uri>());

        if (countryList.get(position).getFlag()==null)return;
        requestBuilder.diskCacheStrategy(DiskCacheStrategy.NONE)
                .load(Uri.parse(countryList.get(position).getFlag()))
                .into(countryflag);


    }

    private void attachView(View layout) {
        countryName = layout.findViewById(R.id.countryName);
        countryflag = layout.findViewById(R.id.countryFlag);
        countryarea =  layout.findViewById(R.id.areasize);
    }

    @Override
    public View getDropDownView(int position, View convertView, ViewGroup parent) {
        return getCustomView(position, convertView, parent);
    }

    // It gets a View that displays the data at the specified position
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        return getCustomView(position, convertView, parent);
    }

}