package com.example.dreamcountry.adapters;

import android.content.Context;
import android.graphics.drawable.PictureDrawable;
import android.net.Uri;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.recyclerview.widget.RecyclerView;

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
import com.example.dreamcountry.model.RegionalBloc;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

public class RecycleViewAdapter extends RecyclerView.Adapter<RecycleViewAdapter.MyViewHolder> {

    List<Country> nearByCountries;
    Context context;

    public RecycleViewAdapter(Context context, List<Country> nearByCountries) {
        this.context = context;
        this.nearByCountries = nearByCountries;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        // infalte the item Layout
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.country_item, parent, false);
        MyViewHolder vh = new MyViewHolder(v); // pass the view to View Holder
        return vh;
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        // set the data in items
        int myposition = holder.getAdapterPosition();
        Log.i("onBindViewHolder", position+".... "+ nearByCountries.get(myposition));

        if (myposition==nearByCountries.size())return;
        if (nearByCountries.get(myposition)==null) return;
        if (nearByCountries.get(myposition).getArea()==null) nearByCountries.get(holder.getAdapterPosition()).setArea((float)0);
        holder.countryName.setText(nearByCountries.get(myposition).getName() + " - "+ nearByCountries.get(myposition).getNativeName());
        holder.countryarea.setText(nearByCountries.get(myposition).getArea().intValue()+ " -area");
        fillImg(holder, myposition);
        //holder.countryarea.setText();
        // implement setOnClickListener event on item view.
        holder.itemView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // display a toast with person name on item click
                Toast.makeText(context,"You can do any thing with this click", Toast.LENGTH_SHORT).show();
            }
        });

    }

    private void fillImg(MyViewHolder holder, int adapterPosition) {
        GenericRequestBuilder<Uri, InputStream, SVG, PictureDrawable> requestBuilder = Glide.with(context)
                .using(Glide.buildStreamModelLoader(Uri.class, context), InputStream.class)
                .from(Uri.class)
                .as(SVG.class)
                .transcode(new SvgDrawableTranscoder(), PictureDrawable.class)
                .sourceEncoder(new StreamEncoder())
                .cacheDecoder(new FileToStreamDecoder<SVG>(new SvgDecoder()))
                .decoder(new SvgDecoder())
                .listener(new SvgSoftwareLayerSetter<Uri>());

        requestBuilder.diskCacheStrategy(DiskCacheStrategy.NONE)
                .load(Uri.parse(nearByCountries.get(adapterPosition).getFlag()))
                .into(holder.countryFlag);


    }


    @Override
    public int getItemCount() {
        return nearByCountries.size();
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        TextView countryName;// init the item view's
        TextView countryarea;// init the item view's
        ImageView countryFlag; //no need for now

        public MyViewHolder(View itemView) {
            super(itemView);

            // get the reference of item view's
            countryName =  itemView.findViewById(R.id.countryName);
            countryFlag =  itemView.findViewById(R.id.countryFlag);
            countryarea =  itemView.findViewById(R.id.areasize);

        }
    }
}